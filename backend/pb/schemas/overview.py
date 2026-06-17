import uuid
from datetime import datetime
from typing import List, Optional
from ninja import Schema

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
