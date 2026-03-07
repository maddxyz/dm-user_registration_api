import secrets
from datetime import datetime, timedelta, timezone

import asyncpg
from fastapi import APIRouter, Depends
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.db.pool import get_db_pool
from app.db.user_repository import UserRepository
from app.exceptions import UserAlreadyExists
from app.schemas.user import UserCreateRequest, UserCreateResponse
from app.services.email import ConsoleEmailService, EmailService

pwd_hash = PasswordHash((BcryptHasher(),))

router = APIRouter(prefix="/users", tags=["users"])


def get_email_service() -> EmailService:
    return ConsoleEmailService()


def get_repository(pool: asyncpg.Pool = Depends(get_db_pool)) -> UserRepository:
    return UserRepository(pool)


def generate_code() -> str:
    return f"{secrets.randbelow(10000):04d}"


@router.post("", status_code=201, response_model=UserCreateResponse)
async def register(
    body: UserCreateRequest,
    repo: UserRepository = Depends(get_repository),
    email_service: EmailService = Depends(get_email_service),
):
    hashed_password = pwd_hash.hash(body.password)

    try:
        user = await repo.create_user(body.email, hashed_password)
    except asyncpg.UniqueViolationError:
        raise UserAlreadyExists()

    code = generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
    await repo.create_activation_code(user.id, code, expires_at)

    await email_service.send_activation_code(body.email, code)

    return UserCreateResponse(id=user.id, email=user.email)
