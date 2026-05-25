import uuid
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from ..models import Board, Column, Task, TaskStatus
from ..schemas import TaskIn, TaskOut, TaskUpdateIn
from ..permissions import has_board_access
from ..services import task_service

router = Router()


@router.get("/boards/{board_id}/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_tasks(
    request,
    board_id: uuid.UUID,
    status: Optional[TaskStatus] = Query(None),
    column_id: Optional[uuid.UUID] = Query(None),
    column_kind: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    return task_service.list_tasks(
        board, status=status, column_id=column_id, column_kind=column_kind,
        priority=priority, assignee=assignee, tag=tag, search=search,
    )


@router.get("/boards/{board_id}/backlog/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_backlog_tasks(
    request,
    board_id: uuid.UUID,
    status: Optional[TaskStatus] = Query(None),
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    return task_service.list_backlog_tasks(
        board, status=status, priority=priority, assignee=assignee, tag=tag, search=search,
    )


@router.get("/columns/{column_id}/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_column_tasks(request, column_id: uuid.UUID, status: Optional[TaskStatus] = Query(None)):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)
    return task_service.list_column_tasks(column, status=status)


@router.get("/tasks/{task_id}", response=TaskOut, auth=JWTAuth())
def get_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)
    return task


@router.post("/boards/{board_id}/tasks", response={201: TaskOut}, auth=JWTAuth())
def create_board_task(request, board_id: uuid.UUID, payload: TaskIn):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    try:
        task = task_service.create_task(board, request.auth, payload)
    except (LookupError, PermissionError) as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return 201, task


@router.post("/columns/{column_id}/tasks", response={201: TaskOut}, auth=JWTAuth())
def create_column_task(request, column_id: uuid.UUID, payload: TaskIn):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)
    payload.column_id = column.id
    try:
        task = task_service.create_task(column.board, request.auth, payload)
    except (LookupError, PermissionError) as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return 201, task


@router.patch("/tasks/{task_id}", response=TaskOut, auth=JWTAuth())
def update_task(request, task_id: uuid.UUID, payload: TaskUpdateIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        return router.api.create_response(request, {"detail": "No permission to edit this task"}, status=403)
    try:
        return task_service.update_task(task, payload)
    except (LookupError, PermissionError) as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)


@router.post("/tasks/{task_id}/archive", response=TaskOut, auth=JWTAuth())
def archive_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)
    return task_service.archive_task(task)


@router.post("/tasks/{task_id}/restore", response=TaskOut, auth=JWTAuth())
def restore_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)
    return task_service.restore_task(task)


@router.delete("/tasks/{task_id}", auth=JWTAuth())
def delete_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        return router.api.create_response(request, {"detail": "No access to this task"}, status=403)
    task_service.delete_task(task)
    return {"success": True, "message": "Task archived"}
