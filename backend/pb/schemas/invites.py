import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema

class InviteIn(Schema):
    """Input for creating a new invite."""
    expires_in_days: int = 7
    max_uses: Optional[int] = None

class InvitePatchIn(Schema):
    """Input for updating an existing invite."""
    expires_in_days: Optional[int] = None
    expire_at: Optional[datetime] = None
    max_uses: Optional[int] = None
    is_active: Optional[bool] = None

class InviteOut(Schema):
    """Full invite response for owner/staff."""
    id: uuid.UUID
    board_id: uuid.UUID
    board_name: str
    invite_code: uuid.UUID
    invite_path: str
    max_uses: Optional[int]
    used_count: int
    expire_at: datetime
    is_active: bool
    created_by_username: Optional[str]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_board_id(obj):
        return obj.board.id

    @staticmethod
    def resolve_board_name(obj):
        return obj.board.name

    @staticmethod
    def resolve_invite_code(obj):
        return obj.id

    @staticmethod
    def resolve_invite_path(obj):
        return f"/api/invites/{obj.id}/join"

    @staticmethod
    def resolve_created_by_username(obj):
        return obj.created_by.username if obj.created_by else None

class InvitePublicOut(Schema):
    """Safe invite info returned to any authenticated user (for join flow)."""
    id: uuid.UUID
    board_name: str
    is_active: bool
    is_expired: bool
    is_exhausted: bool
    invite_path: str

    @staticmethod
    def resolve_board_name(obj):
        return obj.board.name

    @staticmethod
    def resolve_is_expired(obj):
        return obj.is_expired()

    @staticmethod
    def resolve_is_exhausted(obj):
        return obj.is_exhausted()

    @staticmethod
    def resolve_invite_path(obj):
        return f"/api/invites/{obj.id}/join"
