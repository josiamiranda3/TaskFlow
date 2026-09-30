
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.core.db import (
    get_required_env,
    test_connection as check_database_connection,
)

def test_get_required_env_returns_value(monkeypatch):
    monkeypatch.setenv("TEST_DB_VARIABLE", "valor_teste")

    result = get_required_env("TEST_DB_VARIABLE")

    assert result == "valor_teste"


def test_get_required_env_raises_when_variable_is_missing(monkeypatch):
    monkeypatch.delenv("TEST_DB_VARIABLE", raising=False)

    with pytest.raises(
        RuntimeError,
        match="TEST_DB_VARIABLE.*não foi configurada",
    ):
        get_required_env("TEST_DB_VARIABLE")


def test_connection_returns_success_message():
    fake_engine = MagicMock()
    fake_connection = fake_engine.connect.return_value.__enter__.return_value

    with patch("app.core.db.engine", fake_engine):
        result = check_database_connection()

    assert result == "Conexão com PostgreSQL estabelecida."
    fake_connection.execute.assert_called_once()


def test_connection_raises_runtime_error_on_database_failure():
    fake_engine = MagicMock()
    fake_engine.connect.side_effect = SQLAlchemyError(
        "falha simulada"
    )

    with patch("app.core.db.engine", fake_engine):
        with pytest.raises(
            RuntimeError,
            match="Não foi possível estabelecer conexão",
        ) as exc_info:
            check_database_connection()

    assert isinstance(exc_info.value.__cause__, SQLAlchemyError)