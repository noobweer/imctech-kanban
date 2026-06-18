import uuid
from typing import List, Optional
from django.utils import timezone
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django.db.models import Q

from ..models import Task, Board, TaskMentorRequest, TaskMentorRequestStatus, TaskMentorRequestType
from .activity_service import create_log
from .comment_service import create_task_comment
from ..permissions import (
    can_create_mentor_request,
    can_read_mentor_request,
    can_respond_mentor_request,
    can_resolve_mentor_request,
    can_cancel_mentor_request,
    has_board_access,
)

def create_mentor_request(user, task: Task, request_type: str, message: str) -> TaskMentorRequest:
    if not can_create_mentor_request(user, task):
        raise PermissionError("MENTOR_REQUEST_CREATE_FORBIDDEN")

    if not message or not message.strip():
        raise ValueError("MESSAGE_REQUIRED")

    has_active = TaskMentorRequest.objects.filter(
        task=task,
        status__in=[TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]
    ).exists()
    
    if has_active:
        raise ValueError("ACTIVE_MENTOR_REQUEST_ALREADY_EXISTS")

    request_obj = TaskMentorRequest.objects.create(
        task=task,
        created_by=user,
        request_type=request_type,
        message=message.strip()
    )

    create_log(
        board=task.column.board,
        action_type="mentor_request_created",
        metadata={"task_id": str(task.id), "request_id": str(request_obj.id)}
    )

    return request_obj


def get_active_request_for_task(user, task: Task) -> Optional[TaskMentorRequest]:
    if not has_board_access(user, task.column.board):
        raise PermissionError("BOARD_ACCESS_DENIED")

    return TaskMentorRequest.objects.filter(
        task=task,
        status__in=[TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]
    ).first()


def get_mentor_requests_for_board(
    user, 
    board: Board, 
    status_filter: Optional[str] = None, 
    request_type_filter: Optional[str] = None, 
    mine_filter: Optional[bool] = None
) -> List[TaskMentorRequest]:
    
    if not has_board_access(user, board):
        raise PermissionError("BOARD_ACCESS_DENIED")

    qs = TaskMentorRequest.objects.filter(task__column__board=board)

    if status_filter:
        qs = qs.filter(status=status_filter)
    else:
        qs = qs.filter(status__in=[TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS])

    if request_type_filter:
        qs = qs.filter(request_type=request_type_filter)

    if mine_filter:
        qs = qs.filter(created_by=user)

    return list(qs.select_related("task", "created_by", "started_by", "started_comment", "closed_by"))


def get_mentor_request(user, request_id: uuid.UUID) -> TaskMentorRequest:
    request_obj = get_object_or_404(TaskMentorRequest, id=request_id)
    if not can_read_mentor_request(user, request_obj):
        raise PermissionError("MENTOR_REQUEST_READ_FORBIDDEN")
    return request_obj


def respond_to_mentor_request(user, request_obj: TaskMentorRequest, content: str):
    if not can_respond_mentor_request(user, request_obj.task):
        raise PermissionError("MENTOR_REQUEST_RESPOND_FORBIDDEN")

    if request_obj.status not in [TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]:
        raise ValueError("REQUEST_NOT_ACTIVE")

    comment = create_task_comment(user, request_obj.task, content)

    if request_obj.status == TaskMentorRequestStatus.OPEN:
        request_obj.status = TaskMentorRequestStatus.IN_PROGRESS
        request_obj.started_by = user
        request_obj.started_comment = comment
        request_obj.started_at = timezone.now()
        request_obj.save()

        create_log(
            board=request_obj.task.column.board,
            action_type="mentor_request_started",
            metadata={"task_id": str(request_obj.task.id), "request_id": str(request_obj.id)}
        )

    return request_obj, comment


def resolve_mentor_request(user, request_obj: TaskMentorRequest) -> TaskMentorRequest:
    if not can_resolve_mentor_request(user, request_obj):
        raise PermissionError("MENTOR_REQUEST_RESOLVE_FORBIDDEN")

    if request_obj.status not in [TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]:
        raise ValueError("REQUEST_NOT_ACTIVE")

    request_obj.status = TaskMentorRequestStatus.RESOLVED
    request_obj.closed_by = user
    request_obj.closed_at = timezone.now()
    request_obj.save()

    create_log(
        board=request_obj.task.column.board,
        action_type="mentor_request_resolved",
        metadata={"task_id": str(request_obj.task.id), "request_id": str(request_obj.id)}
    )

    return request_obj


def cancel_mentor_request(user, request_obj: TaskMentorRequest, close_reason: Optional[str] = None) -> TaskMentorRequest:
    if not can_cancel_mentor_request(user, request_obj):
        raise PermissionError("MENTOR_REQUEST_CANCEL_FORBIDDEN")

    if request_obj.status not in [TaskMentorRequestStatus.OPEN, TaskMentorRequestStatus.IN_PROGRESS]:
        raise ValueError("REQUEST_NOT_ACTIVE")

    if request_obj.created_by != user and not close_reason:
        raise ValueError("CLOSE_REASON_REQUIRED")

    request_obj.status = TaskMentorRequestStatus.CANCELLED
    request_obj.closed_by = user
    request_obj.closed_at = timezone.now()
    if close_reason:
        request_obj.close_reason = close_reason
    request_obj.save()

    create_log(
        board=request_obj.task.column.board,
        action_type="mentor_request_cancelled",
        metadata={"task_id": str(request_obj.task.id), "request_id": str(request_obj.id)}
    )

    return request_obj

