import uuid
from typing import List, Optional

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from ..models import Board, Column, ColumnStatus
from ..schemas import ColumnIn, ColumnOut, ColumnUpdateIn, ColumnMoveIn
from ..permissions import has_board_access, can_edit_board, can_edit_column
from ..services import column_service

router = Router()


@router.get("/boards/{board_id}/columns", response=List[ColumnOut], auth=JWTAuth())
@paginate
def list_columns(request, board_id: uuid.UUID,
                 status: Optional[ColumnStatus] = Query(None),
                 kind: str = Query("board")):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return router.api.create_response(request, {"detail": "No access to this board"}, status=403)
    return column_service.list_columns(board, status=status, kind=kind)


@router.post("/boards/{board_id}/columns", response={201: ColumnOut}, auth=JWTAuth())
def create_column(request, board_id: uuid.UUID, payload: ColumnIn):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)
    column = column_service.create_column(board, payload)
    return 201, column


@router.post("/boards/{board_id}/columns/defaults", response={201: List[ColumnOut]}, auth=JWTAuth())
def create_default_columns(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return router.api.create_response(request, {"detail": "No permission to edit this board"}, status=403)
    try:
        columns = column_service.create_default_columns(board)
    except ValueError as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return 201, columns


@router.get("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def retrieve_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        return router.api.create_response(request, {"detail": "No access to this column"}, status=403)
    return column


@router.patch("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def update_column(request, column_id: uuid.UUID, payload: ColumnUpdateIn):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return router.api.create_response(request, {"detail": "No permission to edit this column"}, status=403)
    return column_service.update_column(column, payload)


@router.post("/columns/{column_id}/move", response=ColumnOut, auth=JWTAuth())
def move_column(request, column_id: uuid.UUID, payload: ColumnMoveIn):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return router.api.create_response(request, {"detail": "No permission to move this column"}, status=403)
    return column_service.move_column(column, payload.position)


@router.post("/columns/{column_id}/archive", response=ColumnOut, auth=JWTAuth())
def archive_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return router.api.create_response(request, {"detail": "No permission to archive this column"}, status=403)
    return column_service.archive_column(column)


@router.delete("/columns/{column_id}", auth=JWTAuth())
def delete_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return router.api.create_response(request, {"detail": "No permission to delete this column"}, status=403)
    column_service.archive_column(column)
    return {"success": True, "message": "Column archived successfully"}
