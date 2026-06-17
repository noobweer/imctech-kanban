import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema
from ..models import ColumnStatus, ColumnKind

class ColumnIn(Schema):
    name: str
    position: Optional[int] = None

class ColumnOut(Schema):
    id: uuid.UUID
    board_id: uuid.UUID
    board_name: str
    name: str
    kind: ColumnKind
    position: int
    status: ColumnStatus
    sum_tasks: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_board_id(obj):
        return obj.board.id

    @staticmethod
    def resolve_board_name(obj):
        return obj.board.name

class ColumnUpdateIn(Schema):
    name: Optional[str] = None
    status: Optional[ColumnStatus] = None

class ColumnMoveIn(Schema):
    position: int
