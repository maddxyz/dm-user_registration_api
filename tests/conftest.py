from unittest.mock import AsyncMock

import asyncpg
import pytest

from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app
from app.routers.users import get_email_service


@pytest.fixture
async def db_pool():
    pool = await asyncpg.create_pool(dsn=settings.database_url)
    await pool.execute("DELETE FROM activation_codes")
    await pool.execute("DELETE FROM users")
    yield pool
    await pool.close()


@pytest.fixture
async def client(db_pool):
    app.state.db_pool = db_pool

    mock_email = AsyncMock()
    app.dependency_overrides[get_email_service] = lambda: mock_email

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        ac.mock_email = mock_email
        yield ac

    app.dependency_overrides.clear()
