# Import necessary modules
from unittest.mock import MagicMock, patch
import pytest
from etl.staging import save_batch, get_pending_batches, update_batch_status

@patch("etl.staging.get_connection")
def test_save_batch(mock_get_connection):
    """ Tests saving a batch to the staging area. """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchone.return_value = (10,)

    result = save_batch(1, [{"value": 12.5}])

    assert result == 10
    mock_cursor.execute.assert_called_once()

@patch("etl.staging.get_connection")
def test_get_pending_batches(mock_get_connection):
    """ Tests retrieving pending and failed batches. """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (10, 1, [{"value": 12.5}], "pending"),
        (11, 1, [{"value": 15.0}], "failed"),
    ]

    result = get_pending_batches()

    assert len(result) == 2
    assert result[0]["status"] == "pending"
    assert result[1]["status"] == "failed"

@patch("etl.staging.get_connection")
def test_update_batch_status(mock_get_connection):
    """ Tests updating a batch status. """
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_get_connection.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    update_batch_status(10, "completed")

    mock_cursor.execute.assert_called_once()

def test_update_batch_status_invalid():
    """ Tests that an invalid status raises ValueError. """
    with pytest.raises(ValueError, match="Invalid staging status"):
        update_batch_status(10, "invalid")
