from ninja import Schema
from datetime import datetime
from typing import Optional


class RegisterSchema(Schema):
    username: str
    password: str
    name: str
    role: str = 'student'


class UserOutSchema(Schema):
    username: str
    name: str
    role: str
    created_at: datetime
    updated_at: datetime


class UserUpdateSchema(Schema):
    name: Optional[str] = None
    role: Optional[str] = None
    password: Optional[str] = None
