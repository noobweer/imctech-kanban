import uuid
import json
from typing import List, Optional
from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404

from ..models import Task, Board, TaskComment
from ..schemas import (
    TaskCommentCreateIn,
    TaskCommentUpdateIn,
    TaskCommentOut,
    TaskCommentStateOut,
)
from ..services.comment_service import (
    list_task_comments,
    create_task_comment,
    update_task_comment,
    soft_delete_task_comment,
    mark_comments_as_read,
    get_task_comment_state,
    get_board_comments_states,
)
from ..services.ws_service import broadcast_board_event

router = Router(auth=JWTAuth())

def _serialize(schema_cls, obj):
    return json.loads(schema_cls.from_orm(obj).json())

@router.get("/tasks/{task_id}/comments", response=List[TaskCommentOut])
def list_comments(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    return list_task_comments(request.user, task)


@router.post("/tasks/{task_id}/comments", response={201: TaskCommentOut})
def create_comment(request, task_id: uuid.UUID, payload: TaskCommentCreateIn):
    task = get_object_or_404(Task, id=task_id)
    comment = create_task_comment(
        request.user, 
        task, 
        content=payload.content, 
        links=payload.links
    )
    broadcast_board_event(task.column.board_id, "comment.created", _serialize(TaskCommentOut, comment), request.user.id)
    return 201, comment


@router.patch("/comments/{comment_id}", response=TaskCommentOut)
def update_comment(request, comment_id: uuid.UUID, payload: TaskCommentUpdateIn):
    comment = get_object_or_404(TaskComment, id=comment_id)
    comment = update_task_comment(
        request.user, 
        comment, 
        content=payload.content, 
        links=payload.links
    )
    broadcast_board_event(comment.task.column.board_id, "comment.updated", _serialize(TaskCommentOut, comment), request.user.id)
    return comment


@router.delete("/comments/{comment_id}", response=dict)
def delete_comment(request, comment_id: uuid.UUID):
    try:
        comment = TaskComment.objects.get(id=comment_id)
        board_id = comment.task.column.board_id
        soft_delete_task_comment(request.user, comment)
        comment.refresh_from_db()
        broadcast_board_event(board_id, "comment.deleted", {"comment_id": str(comment.id), "task_id": str(comment.task_id)}, request.user.id)
    except TaskComment.DoesNotExist:
        pass
    
    return {"success": True, "message": "Comment deleted"}


@router.post("/tasks/{task_id}/comments/read", response=TaskCommentStateOut)
def mark_comments_read(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    mark_comments_as_read(request.user, task)
    state = get_task_comment_state(request.user, task)
    broadcast_board_event(task.column.board_id, "comments.read_state_updated", _serialize(TaskCommentStateOut, state), request.user.id)
    return state


@router.get("/tasks/{task_id}/comments/state", response=TaskCommentStateOut)
def get_comment_state(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    return get_task_comment_state(request.user, task)


@router.get("/boards/{board_id}/comments/states", response=List[TaskCommentStateOut])
def get_comments_states(request, board_id: uuid.UUID, task_ids: Optional[List[uuid.UUID]] = Query(None)):
    board = get_object_or_404(Board, id=board_id)
    return get_board_comments_states(request.user, board, task_ids=task_ids)
