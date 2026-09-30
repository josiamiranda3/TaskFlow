
from unittest.mock import MagicMock, patch

import pytest

from app.core.dependencies import get_db


def test_get_db_yields_session_and_closes_it():
    fake_session = MagicMock()

    with patch(
        "app.core.dependencies.SessionLocal",
        return_value=fake_session,
    ):
        generator = get_db()

        session = next(generator)

        assert session is fake_session
        fake_session.close.assert_not_called()

        with pytest.raises(StopIteration):
            next(generator)

        fake_session.close.assert_called_once()


def test_get_db_closes_session_when_consumer_raises():
    fake_session = MagicMock()

    with patch(
        "app.core.dependencies.SessionLocal",
        return_value=fake_session,
    ):
        generator = get_db()

        session = next(generator)

        assert session is fake_session

        with pytest.raises(ValueError, match="erro simulado"):
            generator.throw(ValueError("erro simulado"))

        fake_session.close.assert_called_once()