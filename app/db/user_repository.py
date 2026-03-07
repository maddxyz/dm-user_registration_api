from datetime import datetime
from uuid import UUID

import asyncpg

from app.models.user import ActivationCode, User


class UserRepository:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool

    async def create_user(self, email: str, hashed_password: str) -> User:
        row = await self._pool.fetchrow(
            """
            INSERT INTO users (email, hashed_password)
            VALUES ($1, $2)
            RETURNING id, email, hashed_password, is_active, created_at
            """,
            email,
            hashed_password,
        )
        return User(**dict(row))

    async def get_user_by_email(self, email: str) -> User | None:
        row = await self._pool.fetchrow(
            "SELECT id, email, hashed_password, is_active, created_at FROM users WHERE email = $1",
            email,
        )
        return User(**dict(row)) if row else None

    async def create_activation_code(
        self, user_id: UUID, code: str, expires_at: datetime
    ) -> None:
        await self._pool.execute(
            """
            INSERT INTO activation_codes (user_id, code, expires_at)
            VALUES ($1, $2, $3)
            """,
            user_id,
            code,
            expires_at,
        )

    async def get_latest_code_for_user(self, user_id: UUID) -> ActivationCode | None:
        row = await self._pool.fetchrow(
            """
            SELECT id, user_id, code, expires_at, used, created_at
            FROM activation_codes
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 1
            """,
            user_id,
        )
        return ActivationCode(**dict(row)) if row else None

    async def mark_code_used(self, code_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE activation_codes SET used = TRUE WHERE id = $1",
            code_id,
        )

    async def activate_user(self, user_id: UUID) -> None:
        await self._pool.execute(
            "UPDATE users SET is_active = TRUE WHERE id = $1",
            user_id,
        )
