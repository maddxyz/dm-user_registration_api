from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str


class UserCreateResponse(BaseModel):
    id: UUID
    email: str
