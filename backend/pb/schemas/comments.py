import uuid
from datetime import datetime
from typing import List, Optional
from ninja import Schema

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
