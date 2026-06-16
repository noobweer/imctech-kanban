import uuid
from datetime import datetime
from typing import List, Optional

from ninja import Schema
from .models import BoardStatus, ColumnStatus, ColumnKind


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


# --- Invite Schemas ---

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


# --- Members Schemas ---

class MemberOut(Schema):
    """Member representation for the members modal."""
    username: str
    name: str
    role: str
    is_owner: bool


# --- Task Schemas ---

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
        from .services.task_lifecycle import normalize_checklist_data
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


# --- Comment Schemas ---

class TaskCommentCreateIn(Schema):
    content: str
    links: Optional[List[str]] = []


class TaskCommentUpdateIn(Schema):
    content: Optional[str] = None
    links: Optional[List[str]] = None


class TaskCommentOut(Schema):
    id: uuid.UUID
    task_id: uuid.UUID
    owner_username: str
    owner_name: Optional[str] = None
    owner_role: Optional[str] = None
    content: str
    links: List[str]
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_task_id(obj):
        return obj.task.id

    @staticmethod
    def resolve_owner_username(obj):
        return obj.owner.username

    @staticmethod
    def resolve_owner_name(obj):
        profile = getattr(obj.owner, "profile", None)
        return getattr(profile, "name", None) if profile else None

    @staticmethod
    def resolve_owner_role(obj):
        profile = getattr(obj.owner, "profile", None)
        return getattr(profile, "role", None) if profile else None


class TaskCommentStateOut(Schema):
    task_id: uuid.UUID
    comments_count: int
    has_comments: bool
    has_unread_comments: bool
    last_comment_at: Optional[datetime] = None
    comments_state: str

# --- Overview Schemas ---

class ProgressColumnOut(Schema):
    id: uuid.UUID
    name: str
    task_count: int
    percent: int

class ProgressOut(Schema):
    total_tasks: int
    columns: List[ProgressColumnOut]

class ActivityColumnOut(Schema):
    column_id: uuid.UUID
    column_name: str
    task_count: int
    percent: int

class ActivityMemberOut(Schema):
    username: str
    name: str
    columns: List[ActivityColumnOut]

class ActivityOut(Schema):
    period: str
    week_start: str
    week_end: str
    members: List[ActivityMemberOut]

class DeadlineTaskOut(Schema):
    id: uuid.UUID
    title: str
    deadline: datetime
    column: str
    assignees: List[str]
    priority: int
    added_to_board_at: Optional[datetime]

class DeadlinesOut(Schema):
    overdue: List[DeadlineTaskOut]
    due_soon: List[DeadlineTaskOut]

# --- Comment Feed Schemas ---

class CommentFeedTaskOut(Schema):
    id: uuid.UUID
    title: str
    column: str
    priority: int
    deadline: Optional[datetime]
    added_to_board_at: Optional[datetime]
    assignees: List[str]
    comments_count: int
    last_comment_at: Optional[datetime]
    comments_state: str  # none | read | unread

class CommentFeedOut(Schema):
    filter: str
    total: int
    tasks: List[CommentFeedTaskOut]
