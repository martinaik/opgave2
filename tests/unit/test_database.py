# Import necessary modules
import os
import psycopg
import pytest
from unittest.mock import MagicMock, patch
from app.database import create_source, get_connection

def test_create_source_new_source() -> None:
    """ Tests creating a new source in the database. """

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (1,)

    with patch(
        "app.database.get_connection",
        return_value=mock_connection,
    ):
        result = create_source("DMI")

    assert result == 1

def test_create_source_existing_source() -> None:
    """ Tests finding an existing source in the database. """

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [None, (1,)]

    with patch(
        "app.database.get_connection",
        return_value=mock_connection,
    ):
        result = create_source("DMI")

    assert result == 1

def test_create_source_not_found() -> None:
    """ Tests raising an error if the source cannot be found. """

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.side_effect = [None, None]

    with (
        patch(
            "app.database.get_connection",
            return_value=mock_connection,
        ),
        pytest.raises(RuntimeError, match="Could not find source 'DMI'"),
    ):
        create_source("DMI")

def test_get_connection_success() -> None:
    """ Tests that a database connection is established. """

    mock_connection = MagicMock()

    with (
        patch.dict(os.environ, {
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        }),
        patch(
            "app.database.psycopg.connect",
            return_value=mock_connection,
        ) as mock_connect,
    ):
        result = get_connection()

    assert result is mock_connection
    mock_connect.assert_called_once()

def test_get_connection_retries_after_failure() -> None:
    """ Tests retrying after a temporary connection failure."""

    mock_connection = MagicMock()

    with (
        patch.dict(os.environ, {
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        }),
        patch(
            "app.database.psycopg.connect",
            side_effect=[
                psycopg.OperationalError("Temporary failure"),
                mock_connection,
            ],
        ) as mock_connect,
        patch("app.database.time.sleep") as mock_sleep,
    ):
        result = get_connection()

    assert result is mock_connection
    assert mock_connect.call_count == 2
    mock_sleep.assert_called_once_with(5)


def test_get_connection_retries_after_interface_error() -> None:
    """ Tests retrying after a database interface error. """

    mock_connection = MagicMock()

    with (
        patch.dict(os.environ, {
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        }),
        patch(
            "app.database.psycopg.connect",
            side_effect=[
                psycopg.InterfaceError("Temporary interface error"),
                mock_connection,
            ],
        ) as mock_connect,
        patch("app.database.time.sleep") as mock_sleep,
    ):
        result = get_connection()

    assert result is mock_connection
    assert mock_connect.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_get_connection_fails_after_max_retries() -> None:
    """ Tests raising the final connection error. """

    with (
        patch.dict(os.environ, {
            "POSTGRES_HOST": "db",
            "POSTGRES_PORT": "5432",
            "POSTGRES_DB": "test_db",
            "POSTGRES_USER": "test_user",
            "POSTGRES_PASSWORD": "test_password",
        }),
        patch(
            "app.database.psycopg.connect",
            side_effect=psycopg.OperationalError(
                "Database unavailable"
            ),
        ) as mock_connect,
        patch("app.database.time.sleep") as mock_sleep,
        pytest.raises(
            psycopg.OperationalError,
            match="Database unavailable",
        ),
    ):
        get_connection()

    assert mock_connect.call_count == 6
    assert mock_sleep.call_count == 5