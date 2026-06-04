import uuid
from typing import Optional
from django.shortcuts import get_object_or_404
from ninja import Router

from ..models import Board
from ..schemas import ProgressOut, ActivityOut, DeadlinesOut
from ..permissions import has_board_access
from ..services.overview_service import get_progress, get_activity, get_deadlines

router = Router()

@router.get("/{board_id}/overview/progress", response=ProgressOut)
def get_board_progress(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.user, board):
        raise PermissionError("Access denied")
    
    return get_progress(board)


@router.get("/{board_id}/overview/activity", response=ActivityOut)
def get_board_activity(request, board_id: uuid.UUID, period: str = "weekly"):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.user, board):
        raise PermissionError("Access denied")
    
    return get_activity(board, period=period)


@router.get("/{board_id}/overview/deadlines", response=DeadlinesOut)
def get_board_deadlines(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.user, board):
        raise PermissionError("Access denied")
    
    return get_deadlines(board)
