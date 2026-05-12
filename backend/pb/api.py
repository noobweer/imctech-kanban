from typing import List, Optional
import uuid

from django.shortcuts import get_object_or_404
from django.db import models, transaction
from django.db.models import Q
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from .models import Project, Board, BoardStatus, Column, ColumnStatus
from .schemas import (
    ProjectIn,
    ProjectOut,
    BoardIn,
    BoardOut,
    BoardUpdateIn,
    ColumnIn,
    ColumnOut,
    ColumnUpdateIn,
    ColumnMoveIn,
)
from .permissions import (
    has_project_access,
    can_edit_project,
    has_board_access,
    can_edit_board,
    can_edit_column,
)

router = Router(tags=["Projects & Boards"])


# --- Project Endpoints ---


@router.get("/projects", response=List[ProjectOut], auth=JWTAuth())
@paginate
def list_projects(request):
    user = request.auth
    if user.is_staff or user.is_superuser:
        return Project.objects.all()
    return Project.objects.filter(Q(boards__owner=user) | Q(boards__members=user)).distinct()


@router.post("/projects", response={201: ProjectOut}, auth=JWTAuth())
def create_project(request, payload: ProjectIn):
    project = Project.objects.create(name=payload.name)
    return 201, project


@router.get("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def retrieve_project(request, project_id: uuid.UUID):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not has_project_access(user, project):
        return router.api.create_response(request, {"detail": "No access to this project"}, status=403)
    return project


@router.patch("/projects/{project_id}", response=ProjectOut, auth=JWTAuth())
def update_project(request, project_id: uuid.UUID, payload: ProjectIn):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(user, project):
        return router.api.create_response(request, {"detail": "No permission to edit this project"}, status=403)

    project.name = payload.name
    project.save()
    return project


@router.delete("/projects/{project_id}", auth=JWTAuth())
def delete_project(request, project_id: uuid.UUID):
    user = request.auth
    project = get_object_or_404(Project, id=project_id)
    if not can_edit_project(user, project):
        return router.api.create_response(request, {"detail": "No permission to delete this project"}, status=403)

    if project.boards.exists():
        return router.api.create_response(
            request,
            {"detail": "Cannot delete project with associated boards. Delete boards first."},
            status=400,
        )
    project.delete()
    return {"success": True}


# --- Board Endpoints ---


@router.get("/boards", response=List[BoardOut], auth=JWTAuth())
@paginate
def list_boards(request, status: Optional[BoardStatus] = Query(None)):
    user = request.auth
    if user.is_staff or user.is_superuser:
        boards = Board.objects.all()
    else:
        boards = Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    if status:
        boards = boards.filter(status=status)
    return boards


@router.post("/boards", response={201: BoardOut}, auth=JWTAuth())
def create_board(request, payload: BoardIn):
    user = request.auth
    project = None
    if payload.project_id:
        project = get_object_or_404(Project, id=payload.project_id)
        if not has_project_access(user, project):
            return router.api.create_response(request, {"detail": "No access to this project"}, status=403)
    else:
        # Create a new project if project_id is not provided
        # Use same name as board for simplicity as requested (no projects in UI)
        project = Project.objects.create(name=payload.name)

    with transaction.atomic():
        board = Board.objects.create(
            name=payload.name,
            description=payload.description,
            project=project,
            owner=user,
            status=payload.status,
            tasks_total=payload.tasks_total,
            tasks_done=payload.tasks_done,
            progress_percent=payload.progress_percent,
        )
        board.members.add(user)

        # Create columns if provided
        for i, col_data in enumerate(payload.columns):
            Column.objects.create(
                board=board,
                name=col_data.name,
                position=col_data.position if col_data.position is not None else i + 1,
            )

    return 201, board


@router.get("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def retrieve_board(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    return board


@router.patch("/boards/{board_id}", response=BoardOut, auth=JWTAuth())
def update_board(request, board_id: uuid.UUID, payload: BoardUpdateIn):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    if payload.name is not None:
        board.name = payload.name
    if payload.description is not None:
        board.description = payload.description
    if payload.status is not None:
        board.status = payload.status
    board.save()
    return board


@router.delete("/boards/{board_id}", auth=JWTAuth())
def delete_board(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to delete this board"}, status=403)

    # Safe deletion strategy: archive the board
    board.status = BoardStatus.ARCHIVED
    board.save()
    return {"success": True, "message": "Board archived successfully"}


# --- Column Endpoints ---


@router.get("/boards/{board_id}/columns", response=List[ColumnOut], auth=JWTAuth())
@paginate
def list_columns(request, board_id: uuid.UUID, status: Optional[ColumnStatus] = Query(None)):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(user, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)

    columns = board.columns.all()
    if status:
        columns = columns.filter(status=status)
    return columns


@router.post("/boards/{board_id}/columns", response={201: ColumnOut}, auth=JWTAuth())
def create_column(request, board_id: uuid.UUID, payload: ColumnIn):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    with transaction.atomic():
        if payload.position is None:
            max_pos = board.columns.aggregate(models.Max("position"))["position__max"] or 0
            position = max_pos + 1
        else:
            position = payload.position
            # Shift existing columns
            board.columns.filter(position__gte=position).update(position=models.F("position") + 1)

        column = Column.objects.create(
            board=board,
            name=payload.name,
            position=position,
        )
    return 201, column


@router.post("/boards/{board_id}/columns/defaults", response={201: List[ColumnOut]}, auth=JWTAuth())
def create_default_columns(request, board_id: uuid.UUID):
    user = request.auth
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(user, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)

    if board.columns.exists():
        return router.api.create_response(
            request,
            {"detail": "Board already has columns. Cannot create defaults."},
            status=400,
        )

    defaults = [
        {"name": "To Do", "position": 1},
        {"name": "In Progress", "position": 2},
        {"name": "Done", "position": 3},
    ]

    with transaction.atomic():
        columns = [Column.objects.create(board=board, **default) for default in defaults]

    return 201, columns


@router.get("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def retrieve_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(user, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)
    return column


@router.patch("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def update_column(request, column_id: uuid.UUID, payload: ColumnUpdateIn):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to edit this column"}, status=403)

    if payload.name is not None:
        column.name = payload.name
    if payload.status is not None:
        column.status = payload.status
    column.save()
    return column


@router.post("/columns/{column_id}/move", response=ColumnOut, auth=JWTAuth())
def move_column(request, column_id: uuid.UUID, payload: ColumnMoveIn):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to move this column"}, status=403)

    old_position = column.position
    new_position = payload.position

    if old_position == new_position:
        return column

    with transaction.atomic():
        if new_position > old_position:
            # Moving down: shift items between old and new up
            column.board.columns.filter(position__gt=old_position, position__lte=new_position).update(
                position=models.F("position") - 1
            )
        else:
            # Moving up: shift items between new and old down
            column.board.columns.filter(position__gte=new_position, position__lt=old_position).update(
                position=models.F("position") + 1
            )

        column.position = new_position
        column.save()

    return column


@router.post("/columns/{column_id}/archive", response=ColumnOut, auth=JWTAuth())
def archive_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to archive this column"}, status=403)

    column.status = ColumnStatus.ARCHIVED
    column.save()
    return column


@router.delete("/columns/{column_id}", auth=JWTAuth())
def delete_column(request, column_id: uuid.UUID):
    user = request.auth
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(user, column):
        return router.api.create_response(request, {"detail": "No permission to delete this column"}, status=403)

    # Soft delete strategy: archive the column
    column.status = ColumnStatus.ARCHIVED
    column.save()
    return {"success": True, "message": "Column archived successfully"}
