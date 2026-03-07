from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime


@dataclass
class ActivationCode:
    id: UUID
    user_id: UUID
    code: str
    expires_at: datetime
    used: bool
    created_at: datetime
