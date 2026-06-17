import uuid
from datetime import datetime
from ninja import Schema

class ProjectIn(Schema):
    name: str

class ProjectOut(Schema):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime
