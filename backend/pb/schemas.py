import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from .models import BoardStatus, ColumnStatus


# Project Schemas
class ProjectIn(Schema):
    name: str


class ProjectOut(Schema):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime


# Column Schemas
class ColumnIn(Schema):
    name: str
    position: Optional[int] = None


# Board Schemas
class BoardIn(Schema):
    name: str
    description: Optional[str] = None
    project_id: Optional[uuid.UUID] = None
    status: Optional[BoardStatus] = BoardStatus.ACTIVE
    tasks_total: Optional[int] = 0
    tasks_done: Optional[int] = 0
    progress_percent: Optional[int] = 0
    columns: List[ColumnIn] = []


class BoardOut(Schema):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    project_id: Optional[uuid.UUID]
    project_name: Optional[str] = None
    owner_username: str
    members: List[str]
    status: BoardStatus
    tasks_total: int
    tasks_done: int
    progress_percent: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_project_id(obj):
        return obj.project.id if obj.project else None

    @staticmethod
    def resolve_project_name(obj):
        return obj.project.name if obj.project else None

    @staticmethod
    def resolve_owner_username(obj):
        return obj.owner.username

    @staticmethod
    def resolve_members(obj):
        return [member.username for member in obj.members.all()]


class BoardUpdateIn(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BoardStatus] = None


class ColumnOut(Schema):
    id: uuid.UUID
    board_id: uuid.UUID
    board_name: str
    name: str
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
