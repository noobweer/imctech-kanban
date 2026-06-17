import uuid
from datetime import datetime
from typing import Optional
from ninja import Schema
from ..models import TaskMentorRequestType, TaskMentorRequestStatus

class MentorRequestCreateIn(Schema):
    request_type: str
    message: str

class MentorRequestRespondIn(Schema):
    content: str

class MentorRequestCancelIn(Schema):
    close_reason: Optional[str] = None

class MentorRequestOut(Schema):
    id: uuid.UUID
    task_id: uuid.UUID
    task_title: str
    board_id: uuid.UUID
    created_by_id: int
    created_by_username: str
    request_type: str
    status: str
    message: str
    
    started_by_id: Optional[int] = None
    started_by_username: Optional[str] = None
    started_comment_id: Optional[uuid.UUID] = None
    started_at: Optional[datetime] = None
    
    closed_by_id: Optional[int] = None
    closed_by_username: Optional[str] = None
    closed_at: Optional[datetime] = None
    close_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_task_id(obj):
        return obj.task.id

    @staticmethod
    def resolve_task_title(obj):
        return obj.task.title

    @staticmethod
    def resolve_board_id(obj):
        return obj.task.column.board.id

    @staticmethod
    def resolve_created_by_id(obj):
        return obj.created_by.id

    @staticmethod
    def resolve_created_by_username(obj):
        return obj.created_by.username

    @staticmethod
    def resolve_started_by_id(obj):
        return obj.started_by.id if obj.started_by else None

    @staticmethod
    def resolve_started_by_username(obj):
        return obj.started_by.username if obj.started_by else None

    @staticmethod
    def resolve_started_comment_id(obj):
        return obj.started_comment.id if obj.started_comment else None

    @staticmethod
    def resolve_closed_by_id(obj):
        return obj.closed_by.id if obj.closed_by else None

    @staticmethod
    def resolve_closed_by_username(obj):
        return obj.closed_by.username if obj.closed_by else None
