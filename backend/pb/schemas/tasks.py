import uuid
from datetime import datetime
from typing import List, Optional
from ninja import Schema

class ChecklistItem(Schema):
    id: str
    title: str
    is_done: bool
    position: int

class ChecklistItemCreateIn(Schema):
    title: str

class ChecklistItemPatchIn(Schema):
    title: Optional[str] = None
    is_done: Optional[bool] = None

class ChecklistReorderIn(Schema):
    ordered_item_ids: List[str]

class TaskIn(Schema):
    title: str
    content: Optional[str] = ""
    column_id: Optional[uuid.UUID] = None
    priority: Optional[int] = 0
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = []
    checklist: Optional[List[ChecklistItemCreateIn]] = []
    assignees: Optional[List[str]] = []

class TaskUpdateIn(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    column_id: Optional[uuid.UUID] = None
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = None
    checklist: Optional[List[ChecklistItemCreateIn]] = None
    assignees: Optional[List[str]] = None

class TaskPatchIn(Schema):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[int] = None
    deadline: Optional[datetime] = None
    tags: Optional[List[str]] = None

class TaskMoveIn(Schema):
    target_column_id: uuid.UUID
    position: int

class TaskRestoreIn(Schema):
    target_column_id: uuid.UUID
    position: Optional[int] = None

class TaskAssignIn(Schema):
    username: str

class TaskUnassignIn(Schema):
    username: str

class TaskOut(Schema):
    id: uuid.UUID
    board_id: uuid.UUID
    board_name: str
    column_id: uuid.UUID
    column_name: str
    column_kind: str
    title: str
    content: str
    priority: int
    deadline: Optional[datetime]
    assignees: List[str]
    owner_username: str
    position: int
    tags: List[str]
    checklist: List[ChecklistItem]
    checklist_done_count: int
    checklist_total_count: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_board_id(obj):
        return obj.column.board.id

    @staticmethod
    def resolve_board_name(obj):
        return obj.column.board.name

    @staticmethod
    def resolve_column_id(obj):
        return obj.column.id

    @staticmethod
    def resolve_column_name(obj):
        return obj.column.name

    @staticmethod
    def resolve_column_kind(obj):
        return obj.column.kind

    @staticmethod
    def resolve_assignees(obj):
        return [user.username for user in obj.assignees.all()]

    @staticmethod
    def resolve_checklist(obj):
        from ..services.task_lifecycle import normalize_checklist_data
        return normalize_checklist_data(obj.checklist)

    @staticmethod
    def resolve_owner_username(obj):
        return obj.owner.username

    @staticmethod
    def resolve_checklist_done_count(obj):
        if not obj.checklist:
            return 0
        return sum(1 for item in obj.checklist if isinstance(item, dict) and item.get("is_done", False))

    @staticmethod
    def resolve_checklist_total_count(obj):
        if not obj.checklist:
            return 0
        return len(obj.checklist)
