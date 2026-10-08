# Import necessary modules
from unittest.mock import MagicMock, patch
from app.database import create_source

def test_create_source_new_source() -> None:
    """ Tests creating a new source in the database. """

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchone.return_value = (1,)

    with patch(
        "app.database.get_connection",
        return_value=mock_connection
    ):
        result = create_source("DMI")

    assert result == 1

def test_create_source_existing_source() -> None:
    """ Tests creating an existing source in the database. """

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    mock_cursor.fetchone.side_effect = [
        None,
        (1,)
    ]

    with patch(
        "app.database.get_connection",
        return_value=mock_connection
    ):
        result = create_source("DMI")

    assert result == 1