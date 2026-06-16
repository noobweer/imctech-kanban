import uuid
from typing import List
from django.http import JsonResponse

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from ..models import Board
from ..schemas import MemberOut
from ..permissions import has_board_access, can_edit_board
from ..services import member_service

router = Router()


@router.get("/boards/{board_id}/members", response=List[MemberOut], auth=JWTAuth())
def list_board_members(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not has_board_access(request.auth, board):
        return JsonResponse({"detail": "No access to this board"}, status=403)
    return member_service.list_members(board)


@router.delete("/boards/{board_id}/members/{username}", auth=JWTAuth())
def remove_member(request, board_id: uuid.UUID, username: str):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return JsonResponse({"detail": "No permission to remove members"}, status=403)
    try:
        member_service.remove_member(board, username)
    except member_service.User.DoesNotExist as e:
        return JsonResponse({"detail": str(e)}, status=404)
    except LookupError as e:
        return JsonResponse({"detail": str(e)}, status=404)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)
    return {"success": True, "message": f"User '{username}' has been removed from the board"}


@router.post("/boards/{board_id}/leave", auth=JWTAuth())
def leave_board(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    try:
        member_service.leave_board(board, request.auth)
    except ValueError as e:
        return JsonResponse({"detail": str(e)}, status=400)
    return {"success": True, "message": f"You have left the board '{board.name}'"}
