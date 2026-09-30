import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import CurrentUser, get_current_user


@pytest.mark.anyio
async def test_missing_token_returns_401():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token de autenticação não informado."


@pytest.mark.anyio
async def test_invalid_token_returns_401():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    response = MagicMock()
    response.status_code = 401

    client = AsyncMock()
    client.get.return_value = response

    with patch("app.core.security.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == (
        "Token de autenticação inválido ou expirado."
    )


@pytest.mark.anyio
async def test_auth_service_request_error_returns_503():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="some-token",
    )

    client = AsyncMock()
    client.get.side_effect = httpx.ConnectError("connection failed")

    with patch("app.core.security.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == (
        "Serviço de autenticação temporariamente indisponível."
    )


@pytest.mark.anyio
async def test_auth_service_server_error_returns_503():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="some-token",
    )

    response = MagicMock()
    response.status_code = 500

    client = AsyncMock()
    client.get.return_value = response

    with patch("app.core.security.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == (
        "Não foi possível validar a autenticação."
    )


@pytest.mark.anyio
async def test_invalid_auth_service_response_returns_401():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="some-token",
    )

    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": "not-a-uuid",
        "email": "test@example.com",
    }

    client = AsyncMock()
    client.get.return_value = response

    with patch("app.core.security.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Resposta de autenticação inválida."


@pytest.mark.anyio
async def test_valid_token_returns_current_user():
    user_id = uuid.uuid4()

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": str(user_id),
        "email": "test@example.com",
    }

    client = AsyncMock()
    client.get.return_value = response

    with patch("app.core.security.httpx.AsyncClient") as client_class:
        client_class.return_value.__aenter__.return_value = client

        user = await get_current_user(credentials=credentials)

    assert isinstance(user, CurrentUser)
    assert user.id == user_id
    assert user.email == "test@example.com"