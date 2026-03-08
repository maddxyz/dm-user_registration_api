import base64
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


def basic_auth_header(email: str, password: str) -> dict:
    credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}


async def register_user(client, email="user@test.com", password="secret123"):
    return await client.post(
        "/users",
        json={"email": email, "password": password},
    )


async def test_register_user(client):
    response = await register_user(client)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "user@test.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


async def test_register_sends_email(client):
    await register_user(client)
    client.mock_email.send_activation_code.assert_called_once()
    call_args = client.mock_email.send_activation_code.call_args
    assert call_args[0][0] == "user@test.com"
    assert len(call_args[0][1]) == 4


async def test_register_duplicate_email(client):
    await register_user(client)
    response = await register_user(client)
    assert response.status_code == 409
    assert response.json()["code"] == "USER_ALREADY_EXISTS"


async def test_register_invalid_email(client):
    response = await client.post(
        "/users",
        json={"email": "notanemail", "password": "secret123"},
    )
    assert response.status_code == 422


async def test_activate_success(client, db_pool):
    await register_user(client)
    code = client.mock_email.send_activation_code.call_args[0][1]

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header("user@test.com", "secret123"),
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Account activated successfully"

    row = await db_pool.fetchrow("SELECT is_active FROM users WHERE email = $1", "user@test.com")
    assert row["is_active"] is True


async def test_activate_wrong_password(client):
    await register_user(client)
    code = client.mock_email.send_activation_code.call_args[0][1]

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header("user@test.com", "wrongpassword"),
    )
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


async def test_activate_wrong_email(client):
    await register_user(client)
    code = client.mock_email.send_activation_code.call_args[0][1]

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header("nobody@test.com", "secret123"),
    )
    assert response.status_code == 401


async def test_activate_wrong_code(client):
    await register_user(client)

    response = await client.post(
        "/users/activate",
        json={"code": "0000"},
        headers=basic_auth_header("user@test.com", "secret123"),
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CODE"


async def test_activate_expired_code(client):
    await register_user(client)
    code = client.mock_email.send_activation_code.call_args[0][1]

    expired_time = datetime.now(timezone.utc) + timedelta(seconds=61)
    with patch("app.routers.users.datetime") as mock_dt:
        mock_dt.now.return_value = expired_time

        response = await client.post(
            "/users/activate",
            json={"code": code},
            headers=basic_auth_header("user@test.com", "secret123"),
        )
    assert response.status_code == 410
    assert response.json()["code"] == "CODE_EXPIRED"


async def test_activate_already_used_code(client):
    await register_user(client)
    code = client.mock_email.send_activation_code.call_args[0][1]

    await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header("user@test.com", "secret123"),
    )

    response = await client.post(
        "/users/activate",
        json={"code": code},
        headers=basic_auth_header("user@test.com", "secret123"),
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CODE"
