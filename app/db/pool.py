import asyncpg
from fastapi import Request

from app.config import settings


async def create_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=settings.database_url)


async def close_pool(pool: asyncpg.Pool) -> None:
    await pool.close()


def get_db_pool(request: Request) -> asyncpg.Pool:
    return request.app.state.db_pool
