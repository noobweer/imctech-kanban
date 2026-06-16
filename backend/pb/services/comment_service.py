import uuid
from typing import List, Optional
from django.utils import timezone
from django.db.models import Max
from django.shortcuts import get_object_or_404

from ..models import Task, Board, TaskComment, TaskCommentReadState, ColumnKind, ColumnStatus
from django.db.models import Q
from ..permissions import (
    can_read_task_comments,
    can_create_task_comment,
    can_edit_task_comment,
    can_delete_task_comment,
    has_board_access,
    is_mentor,
)


def list_task_comments(user, task: Task) -> List[TaskComment]:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    return list(task.comments.filter(is_deleted=False))


def create_task_comment(user, task: Task, content: str, links: Optional[List[str]] = None) -> TaskComment:
    if not can_create_task_comment(user, task):
        raise PermissionError("COMMENT_CREATE_FORBIDDEN")

    if not content or not content.strip():
        raise ValueError("COMMENT_CONTENT_REQUIRED")

    comment = TaskComment.objects.create(
        task=task,
        owner=user,
        content=content.strip(),
        links=links or []
    )

    # Update read state for the author
    mark_comments_as_read(user, task)

    return comment


def update_task_comment(user, comment: TaskComment, content: Optional[str] = None, links: Optional[List[str]] = None) -> TaskComment:
    if comment.is_deleted:
        raise ValueError("COMMENT_NOT_FOUND")

    if not can_edit_task_comment(user, comment):
        raise PermissionError("COMMENT_EDIT_FORBIDDEN")

    if content is not None:
        if not content or not content.strip():
            raise ValueError("COMMENT_CONTENT_REQUIRED")
        comment.content = content.strip()

    if links is not None:
        comment.links = links

    comment.save()
    return comment


def soft_delete_task_comment(user, comment: TaskComment) -> None:
    if comment.is_deleted:
        return

    if not can_delete_task_comment(user, comment):
        raise PermissionError("COMMENT_DELETE_FORBIDDEN")

    comment.is_deleted = True
    comment.deleted_at = timezone.now()
    comment.save()


def mark_comments_as_read(user, task: Task) -> TaskCommentReadState:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    state, created = TaskCommentReadState.objects.update_or_create(
        task=task,
        user=user,
        defaults={"last_read_at": timezone.now()}
    )
    return state


def get_task_comment_state(user, task: Task) -> dict:
    if not can_read_task_comments(user, task):
        raise PermissionError("BOARD_ACCESS_DENIED")

    # To avoid N+1 when called from get_board_comments_states (if prefetched),
    # we filter in Python if possible, but for simplicity let's rely on Django cache or manager
    # Since we need to work with both single task and list of tasks, we do it safely:
    all_comments = task.comments.all()
    active_comments = [c for c in all_comments if not c.is_deleted]
    comments_count = len(active_comments)

    if comments_count == 0:
        return {
            "task_id": task.id,
            "comments_count": 0,
            "has_comments": False,
            "has_unread_comments": False,
            "last_comment_at": None,
            "comments_state": "none"
        }

    last_comment_at = max(c.created_at for c in active_comments)
    
    # Get read state for this user
    all_read_states = task.comment_read_states.all()
    read_state = next((rs for rs in all_read_states if rs.user_id == user.id), None)

    if not read_state:
        has_others_comments = any(c.owner_id != user.id for c in active_comments)
        has_unread = has_others_comments
    else:
        has_unread = any(
            c.created_at > read_state.last_read_at and c.owner_id != user.id
            for c in active_comments
        )

    comments_state = "unread" if has_unread else "read"

    return {
        "task_id": task.id,
        "comments_count": comments_count,
        "has_comments": True,
        "has_unread_comments": has_unread,
        "last_comment_at": last_comment_at,
        "comments_state": comments_state
    }


def get_board_comments_states(user, board: Board, task_ids: Optional[List[uuid.UUID]] = None) -> List[dict]:
    if not has_board_access(user, board):
        raise PermissionError("BOARD_ACCESS_DENIED")

    # Efficient fetching
    qs = Task.objects.filter(column__board=board)
    if task_ids is not None:
        qs = qs.filter(id__in=task_ids)

    qs = qs.prefetch_related("comments", "comment_read_states")
    
    states = []
    for task in qs:
        states.append(get_task_comment_state(user, task))

    return states


def get_comments_feed(board: Board, user, filter_type: str) -> dict:
    if not has_board_access(user, board):
        raise PermissionError("BOARD_ACCESS_DENIED")

    # Exclude archived columns
    base_qs = Task.objects.filter(
        column__board=board
    ).exclude(
        column__kind=ColumnKind.ARCHIVE
    ).exclude(
        column__status=ColumnStatus.ARCHIVED
    )

    feed_tasks = []

    if filter_type == "new":
        if is_mentor(user):
            # Mentor sees tasks where they have commented
            qs = base_qs.filter(comments__owner=user, comments__is_deleted=False)
        else:
            # Student sees tasks where they are assignee
            qs = base_qs.filter(assignees=user, comments__is_deleted=False)
            
        qs = qs.distinct().prefetch_related("comments", "comment_read_states", "assignees", "column")

        for task in qs:
            state = get_task_comment_state(user, task)
            if state["comments_state"] == "unread":
                feed_tasks.append({
                    "task": task,
                    "state": state
                })

    elif filter_type == "activity":
        q_commented = Q(comments__owner=user, comments__is_deleted=False)
        q_assigned = Q(assignees=user, comments__is_deleted=False)

        qs = base_qs.filter(q_commented | q_assigned).distinct()
        qs = qs.prefetch_related("comments", "comment_read_states", "assignees", "column")

        for task in qs:
            state = get_task_comment_state(user, task)
            feed_tasks.append({
                "task": task,
                "state": state
            })

    else:
        raise ValueError("Invalid filter_type")

    # Sort by last_comment_at descending
    feed_tasks = [t for t in feed_tasks if t["state"]["last_comment_at"] is not None]
    feed_tasks.sort(key=lambda x: x["state"]["last_comment_at"], reverse=True)

    out_tasks = [
        {
            "id": item["task"].id,
            "title": item["task"].title,
            "column": item["task"].column.name,
            "priority": item["task"].priority,
            "deadline": item["task"].deadline,
            "added_to_board_at": item["task"].added_to_board_at,
            "assignees": [a.username for a in item["task"].assignees.all()],
            "comments_count": item["state"]["comments_count"],
            "last_comment_at": item["state"]["last_comment_at"],
            "comments_state": item["state"]["comments_state"],
        }
        for item in feed_tasks
    ]

    return {
        "filter": filter_type,
        "total": len(out_tasks),
        "tasks": out_tasks
    }

