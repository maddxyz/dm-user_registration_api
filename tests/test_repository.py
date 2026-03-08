from datetime import datetime, timedelta, timezone

import asyncpg
import pytest

from app.db.user_repository import UserRepository


async def test_create_user(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.create_user("test@test.com", "hashedpw")
    assert user.email == "test@test.com"
    assert user.hashed_password == "hashedpw"
    assert user.is_active is False
    assert user.id is not None


async def test_create_user_duplicate_email(db_pool):
    repo = UserRepository(db_pool)
    await repo.create_user("dup@test.com", "hashedpw")
    with pytest.raises(asyncpg.UniqueViolationError):
        await repo.create_user("dup@test.com", "hashedpw2")


async def test_get_user_by_email(db_pool):
    repo = UserRepository(db_pool)
    await repo.create_user("find@test.com", "hashedpw")
    user = await repo.get_user_by_email("find@test.com")
    assert user is not None
    assert user.email == "find@test.com"


async def test_get_user_by_email_not_found(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.get_user_by_email("nobody@test.com")
    assert user is None


async def test_create_and_get_activation_code(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.create_user("code@test.com", "hashedpw")
    expires = datetime.now(timezone.utc) + timedelta(seconds=60)
    await repo.create_activation_code(user.id, "1234", expires)

    code = await repo.get_latest_code_for_user(user.id)
    assert code is not None
    assert code.code == "1234"
    assert code.used is False


async def test_get_latest_code_returns_most_recent(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.create_user("latest@test.com", "hashedpw")
    expires = datetime.now(timezone.utc) + timedelta(seconds=60)
    await repo.create_activation_code(user.id, "1111", expires)
    await repo.create_activation_code(user.id, "2222", expires)

    code = await repo.get_latest_code_for_user(user.id)
    assert code.code == "2222"


async def test_mark_code_used(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.create_user("used@test.com", "hashedpw")
    expires = datetime.now(timezone.utc) + timedelta(seconds=60)
    await repo.create_activation_code(user.id, "5678", expires)

    code = await repo.get_latest_code_for_user(user.id)
    await repo.mark_code_used(code.id)

    code = await repo.get_latest_code_for_user(user.id)
    assert code.used is True


async def test_activate_user(db_pool):
    repo = UserRepository(db_pool)
    user = await repo.create_user("activate@test.com", "hashedpw")
    assert user.is_active is False

    await repo.activate_user(user.id)

    user = await repo.get_user_by_email("activate@test.com")
    assert user.is_active is True
