import uuid
import json
from typing import List, Optional
from django.http import JsonResponse

from django.shortcuts import get_object_or_404
from ninja import Router, Query
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth

from ..models import Board, Column, ColumnStatus
from ..schemas import ColumnIn, ColumnOut, ColumnUpdateIn, ColumnMoveIn
from ..permissions import has_board_access, can_edit_board, can_edit_column
from ..services import column_service, archive_service
from ..services.ws_service import broadcast_board_event

router = Router()

def _serialize(schema_cls, obj):
    return json.loads(schema_cls.from_orm(obj).json())


@router.get("/boards/{board_id}/columns", response=List[ColumnOut], auth=JWTAuth())
@paginate
def list_columns(request, board_id: uuid.UUID,
                 status: Optional[ColumnStatus] = Query(None),
                 kind: str = Query("board")):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    return column_service.list_columns(board, status=status, kind=kind)


@router.post("/boards/{board_id}/columns", response={201: ColumnOut}, auth=JWTAuth())
def create_column(request, board_id: uuid.UUID, payload: ColumnIn):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return JsonResponse({"detail": "No permission to edit this board"}, status=403)
    column = column_service.create_column(board, payload)
    broadcast_board_event(board.id, "column.created", _serialize(ColumnOut, column), request.auth.id)
    return 201, column


@router.post("/boards/{board_id}/columns/defaults", response={201: List[ColumnOut]}, auth=JWTAuth())
def create_default_columns(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return JsonResponse({"detail": "No permission to edit this board"}, status=403)
    try:
        columns = column_service.create_default_columns(board)
        for col in columns:
            broadcast_board_event(board.id, "column.created", _serialize(ColumnOut, col), request.auth.id)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)
    return 201, columns


@router.get("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def retrieve_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        return JsonResponse({"detail": "No access to this column"}, status=403)
    return column


@router.patch("/columns/{column_id}", response=ColumnOut, auth=JWTAuth())
def update_column(request, column_id: uuid.UUID, payload: ColumnUpdateIn):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return JsonResponse({"detail": "No permission to edit this column"}, status=403)
    column = column_service.update_column(column, payload)
    broadcast_board_event(column.board_id, "column.updated", _serialize(ColumnOut, column), request.auth.id)
    return column


@router.post("/columns/{column_id}/move", response=ColumnOut, auth=JWTAuth())
def move_column(request, column_id: uuid.UUID, payload: ColumnMoveIn):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return JsonResponse({"detail": "No permission to move this column"}, status=403)
    column = column_service.move_column(column, payload.position)
    broadcast_board_event(column.board_id, "column.moved", _serialize(ColumnOut, column), request.auth.id)
    return column


@router.post("/columns/{column_id}/archive", response=ColumnOut, auth=JWTAuth())
def archive_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return JsonResponse({"detail": "No permission to archive this column"}, status=403)
    try:
        column = archive_service.archive_column(column)
        broadcast_board_event(column.board_id, "column.archived", _serialize(ColumnOut, column), request.auth.id)
        return column
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)


@router.post("/columns/{column_id}/restore", response=ColumnOut, auth=JWTAuth())
def restore_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return JsonResponse({"detail": "No permission to restore this column"}, status=403)
    column = archive_service.restore_column(column)
    broadcast_board_event(column.board_id, "column.restored", _serialize(ColumnOut, column), request.auth.id)
    return column


@router.delete("/columns/{column_id}", auth=JWTAuth())
def delete_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not can_edit_column(request.auth, column):
        return JsonResponse({"detail": "No permission to delete this column"}, status=403)
    try:
        archive_service.archive_column(column)
        column.refresh_from_db()
        broadcast_board_event(column.board_id, "column.archived", _serialize(ColumnOut, column), request.auth.id)
        return {"success": True, "message": "Column archived successfully"}
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)


@router.post("/columns/{column_id}/clear", auth=JWTAuth())
def clear_column(request, column_id: uuid.UUID):
    column = get_object_or_404(Column, id=column_id)
    if not has_board_access(request.auth, column.board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    try:
        result = archive_service.clear_column(column)
        broadcast_board_event(column.board_id, "column.cleared", {"column_id": str(column.id)}, request.auth.id)
        return result
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)
