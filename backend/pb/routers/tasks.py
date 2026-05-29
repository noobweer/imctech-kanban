import uuid
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth
from ninja.errors import HttpError

from ..models import Board, Column, Task
from ..schemas import (
    TaskIn, TaskOut, TaskPatchIn, TaskMoveIn, TaskAssignIn, TaskUnassignIn,
    ChecklistItemCreateIn, ChecklistItemPatchIn, ChecklistReorderIn, TaskRestoreIn
)
from ..permissions import has_board_access
from ..services import task_service, task_lifecycle, archive_service

router = Router()


@router.get("/boards/{board_id}/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_tasks(
    request,
    board_id: uuid.UUID,
    column_id: Optional[uuid.UUID] = Query(None),
    column_kind: Optional[str] = Query(None),
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        raise HttpError(403, "No access to this board")
    return task_service.list_tasks(
        board, column_id=column_id, column_kind=column_kind,
        priority=priority, assignee=assignee, tag=tag, search=search,
    )


@router.get("/boards/{board_id}/backlog/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_backlog_tasks(
    request,
    board_id: uuid.UUID,
    priority: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        raise HttpError(403, "No access to this board")
    return task_service.list_backlog_tasks(
        board, priority=priority, assignee=assignee, tag=tag, search=search,
    )


@router.get("/columns/{column_id}/tasks", response=List[TaskOut], auth=JWTAuth())
@paginate
def list_column_tasks(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        raise HttpError(403, "No access to this column")
    return task_service.list_column_tasks(column)


@router.get("/tasks/{task_id}", response=TaskOut, auth=JWTAuth())
def get_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    return task


@router.post("/boards/{board_id}/tasks", response={201: TaskOut}, auth=JWTAuth())
def create_board_task(request, board_id: uuid.UUID, payload: TaskIn):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        raise HttpError(403, "No access to this board")
    try:
        task = task_service.create_task(board, request.auth, payload)
    except (LookupError, PermissionError) as e:
        raise HttpError(400, str(e))
    return 201, task


@router.post("/columns/{column_id}/tasks", response={201: TaskOut}, auth=JWTAuth())
def create_column_task(request, column_id: uuid.UUID, payload: TaskIn):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        raise HttpError(403, "No access to this column")
    payload.column_id = column.id
    try:
        task = task_service.create_task(column.board, request.auth, payload)
    except (LookupError, PermissionError) as e:
        raise HttpError(400, str(e))
    return 201, task


@router.patch("/tasks/{task_id}", response=TaskOut, auth=JWTAuth())
def update_task(request, task_id: uuid.UUID, payload: TaskPatchIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No permission to edit this task")
    try:
        return task_service.update_task(task, payload)
    except (LookupError, PermissionError) as e:
        raise HttpError(400, str(e))


@router.post("/tasks/{task_id}/checklist/items", response=TaskOut, auth=JWTAuth())
def add_checklist_item(request, task_id: uuid.UUID, payload: ChecklistItemCreateIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.add_checklist_item(task, payload.title)
    except ValueError as e:
        raise HttpError(400, str(e))


@router.patch("/tasks/{task_id}/checklist/items/{item_id}", response=TaskOut, auth=JWTAuth())
def update_checklist_item(request, task_id: uuid.UUID, item_id: str, payload: ChecklistItemPatchIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.patch_checklist_item(task, item_id, payload.title, payload.is_done)
    except LookupError as e:
        raise HttpError(404, str(e))
    except ValueError as e:
        raise HttpError(400, str(e))


@router.post("/tasks/{task_id}/checklist/items/{item_id}/toggle", response=TaskOut, auth=JWTAuth())
def toggle_checklist_item(request, task_id: uuid.UUID, item_id: str):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.toggle_checklist_item(task, item_id)
    except LookupError as e:
        raise HttpError(404, str(e))


@router.post("/tasks/{task_id}/checklist/items/{item_id}/delete", response=TaskOut, auth=JWTAuth())
def delete_checklist_item(request, task_id: uuid.UUID, item_id: str):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.delete_checklist_item(task, item_id)
    except LookupError as e:
        raise HttpError(404, str(e))


@router.post("/tasks/{task_id}/checklist/reorder", response=TaskOut, auth=JWTAuth())
def reorder_checklist(request, task_id: uuid.UUID, payload: ChecklistReorderIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.reorder_checklist(task, payload.ordered_item_ids)
    except ValueError as e:
        raise HttpError(400, str(e))


@router.post("/tasks/{task_id}/assign", response=TaskOut, auth=JWTAuth())
def assign_task(request, task_id: uuid.UUID, payload: TaskAssignIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.assign_task(task, payload.username)
    except LookupError as e:
        raise HttpError(404, str(e))
    except PermissionError as e:
        raise HttpError(400, str(e))


@router.post("/tasks/{task_id}/unassign", response=TaskOut, auth=JWTAuth())
def unassign_task(request, task_id: uuid.UUID, payload: TaskUnassignIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return task_lifecycle.unassign_task(task, payload.username)
    except LookupError as e:
        raise HttpError(404, str(e))


@router.post("/tasks/{task_id}/move", auth=JWTAuth())
def move_task(request, task_id: uuid.UUID, payload: TaskMoveIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        result = task_lifecycle.move_task(task, payload.target_column_id, payload.position)
        return {
            "task": {
                "id": str(result["task"].id),
                "column_id": str(result["task"].column_id),
                "position": result["task"].position
            },
            "affected_column_ids": result["affected_column_ids"],
            "reordered_tasks": result["reordered_tasks"]
        }
    except LookupError as e:
        raise HttpError(404, str(e))
    except ValueError as e:
        raise HttpError(400, str(e))


@router.post("/tasks/{task_id}/archive", response=TaskOut, auth=JWTAuth())
def archive_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    return archive_service.archive_task(task)


@router.post("/tasks/{task_id}/restore", response=TaskOut, auth=JWTAuth())
def restore_task(request, task_id: uuid.UUID, payload: TaskRestoreIn):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    try:
        return archive_service.restore_task(task, payload.target_column_id, payload.position)
    except ValueError as e:
        raise HttpError(400, str(e))


@router.delete("/tasks/{task_id}", auth=JWTAuth())
def delete_task(request, task_id: uuid.UUID):
    task = get_object_or_404(Task, id=task_id)
    if not has_board_access(request.auth, task.column.board):
        raise HttpError(403, "No access to this task")
    archive_service.archive_task(task)
    return {"success": True, "message": "Task archived"}
