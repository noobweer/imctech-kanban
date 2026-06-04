from datetime import timedelta

from django.db import models, transaction
from django.utils import timezone

from ..models import Board, Invite
from ..schemas import InviteIn, InvitePatchIn
from .activity_service import create_log


def list_invites(board: Board):
    return list(board.invites.select_related("board", "created_by").all())


def get_current_invite(board: Board) -> Invite:
    invite = board.invites.filter(is_active=True).select_related("board", "created_by").first()
    if not invite:
        raise Invite.DoesNotExist("No active invite found for this board.")
    return invite


def get_invite(invite_id) -> Invite:
    return Invite.objects.select_related("board", "created_by").get(id=invite_id)


def create_invite(board: Board, user, payload: InviteIn) -> Invite:
    if payload.expires_in_days <= 0:
        raise ValueError("expires_in_days must be positive.")
    if payload.max_uses is not None and payload.max_uses <= 0:
        raise ValueError("max_uses must be a positive number or null (Unlimited).")

    with transaction.atomic():
        board.invites.filter(is_active=True).update(is_active=False)
        invite = Invite.objects.create(
            board=board,
            max_uses=payload.max_uses,
            used_count=0,
            expire_at=timezone.now() + timedelta(days=payload.expires_in_days),
            is_active=True,
            created_by=user,
        )
    return invite


def patch_invite(invite: Invite, payload: InvitePatchIn) -> Invite:
    if payload.max_uses is not None:
        if payload.max_uses == 0:
            raise ValueError("max_uses cannot be 0. Use null for unlimited.")
        if payload.max_uses < invite.used_count:
            raise ValueError(
                f"max_uses ({payload.max_uses}) cannot be less than used_count ({invite.used_count})."
            )
        invite.max_uses = payload.max_uses
    elif "max_uses" in payload.model_fields_set:
        invite.max_uses = None

    if payload.expires_in_days is not None:
        if payload.expires_in_days <= 0:
            raise ValueError("expires_in_days must be positive.")
        invite.expire_at = timezone.now() + timedelta(days=payload.expires_in_days)
    elif payload.expire_at is not None:
        if payload.is_active is not False and payload.expire_at <= timezone.now():
            raise ValueError("expire_at must be in the future for an active invite.")
        invite.expire_at = payload.expire_at

    if payload.is_active is not None:
        invite.is_active = payload.is_active

    invite.save()
    return invite


def deactivate_invite(invite: Invite) -> None:
    invite.is_active = False
    invite.save()


def join_board(invite: Invite, user) -> Board:
    if not invite.is_active:
        raise ValueError("This invite is no longer active.")
    if invite.is_expired():
        raise ValueError("This invite has expired.")
    if invite.is_exhausted():
        raise ValueError("This invite has reached its maximum number of uses.")

    board = invite.board

    if board.owner == user:
        raise LookupError("already_owner")
    if board.members.filter(id=user.id).exists():
        raise LookupError("already_member")

    with transaction.atomic():
        board.members.add(user)
        Invite.objects.filter(id=invite.id).update(used_count=models.F("used_count") + 1)
        
        create_log(
            board=board,
            action_type="member_joined",
            metadata={"username": user.username}
        )

    return board
