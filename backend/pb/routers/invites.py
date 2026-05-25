import uuid
from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from ..models import Board, Invite
from ..schemas import InviteIn, InvitePatchIn, InviteOut, InvitePublicOut
from ..permissions import can_edit_board
from ..services import invite_service

router = Router()


@router.get("/boards/{board_id}/invites", response=List[InviteOut], auth=JWTAuth())
def list_board_invites(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return router.api.create_response(request, {"detail": "No permission to view invites"}, status=403)
    return invite_service.list_invites(board)


@router.get("/boards/{board_id}/invites/current", response=InviteOut, auth=JWTAuth())
def get_current_invite(request, board_id: uuid.UUID):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return router.api.create_response(request, {"detail": "No permission to view invites"}, status=403)
    try:
        return invite_service.get_current_invite(board)
    except Invite.DoesNotExist:
        return router.api.create_response(request, {"detail": "No active invite found for this board"}, status=404)


@router.post("/boards/{board_id}/invites", response={201: InviteOut}, auth=JWTAuth())
def create_invite(request, board_id: uuid.UUID, payload: InviteIn):
    board = get_object_or_404(Board, id=board_id)
    if not can_edit_board(request.auth, board):
        return router.api.create_response(request, {"detail": "No permission to create invites"}, status=403)
    try:
        invite = invite_service.create_invite(board, request.auth, payload)
    except ValueError as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return 201, invite


@router.get("/invites/{invite_id}", auth=JWTAuth())
def get_invite(request, invite_id: uuid.UUID):
    try:
        invite = invite_service.get_invite(invite_id)
    except Invite.DoesNotExist:
        return router.api.create_response(request, {"detail": "Not found"}, status=404)
    if can_edit_board(request.auth, invite.board):
        return InviteOut.from_orm(invite)
    return InvitePublicOut.from_orm(invite)


@router.patch("/invites/{invite_id}", response=InviteOut, auth=JWTAuth())
def patch_invite(request, invite_id: uuid.UUID, payload: InvitePatchIn):
    invite = get_object_or_404(Invite.objects.select_related("board", "created_by"), id=invite_id)
    if not can_edit_board(request.auth, invite.board):
        return router.api.create_response(request, {"detail": "No permission to update this invite"}, status=403)
    try:
        return invite_service.patch_invite(invite, payload)
    except ValueError as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)


@router.delete("/invites/{invite_id}", auth=JWTAuth())
def deactivate_invite(request, invite_id: uuid.UUID):
    invite = get_object_or_404(Invite.objects.select_related("board"), id=invite_id)
    if not can_edit_board(request.auth, invite.board):
        return router.api.create_response(request, {"detail": "No permission to deactivate this invite"}, status=403)
    invite_service.deactivate_invite(invite)
    return {"success": True, "message": "Invite deactivated"}


@router.post("/invites/{invite_id}/join", auth=JWTAuth())
def join_board_via_invite(request, invite_id: uuid.UUID):
    invite = get_object_or_404(Invite.objects.select_related("board"), id=invite_id)
    try:
        board = invite_service.join_board(invite, request.auth)
    except LookupError as e:
        key = str(e)
        if key == "already_owner":
            return router.api.create_response(request, {"detail": "You are already the owner of this board"}, status=200)
        return router.api.create_response(request, {"detail": "You are already a member of this board"}, status=200)
    except ValueError as e:
        return router.api.create_response(request, {"detail": str(e)}, status=400)
    return {"success": True, "message": f"You have joined the board '{board.name}'"}
