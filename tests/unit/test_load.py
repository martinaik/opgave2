# Import necessary modules
import psycopg
import pytest
from unittest.mock import MagicMock, patch
from etl.load import load_observation

def test_load_observation() -> None:
    """ Tests loading an observation into the database. """

    observation = {
        "station_id": "06110",
        "latitude": 55.7,
        "longitude": 9.5,
        "source_id": 1,
        "observed": "2026-10-02T08:10:00Z",
        "temp_dry": 12.5,
        "humidity": 75.0,
    }

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    with patch(
        "etl.load.get_connection",
        return_value=mock_connection,
    ):
        load_observation(observation)

    assert mock_cursor.execute.call_count == 2

def test_load_observation_retries_after_database_error() -> None:
    """ Tests retrying when a temporary database error occurs. """

    observation = {
        "station_id": "06110",
        "latitude": 55.7,
        "longitude": 9.5,
        "source_id": 1,
        "observed": "2026-10-02T08:10:00Z",
        "temp_dry": 12.5,
        "humidity": 75.0,
    }

    with (
        patch(
            "etl.load.load_observation_once",
            side_effect=[
                psycopg.OperationalError("Temporary failure"),
                None,
            ],
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
    ):
        load_observation(observation)

    assert mock_load.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_load_observation_fails_after_max_retries() -> None:
    """ Tests raising an error after all retry attempts fail. """

    observation = {
        "station_id": "06110",
        "latitude": 55.7,
        "longitude": 9.5,
        "source_id": 1,
        "observed": "2026-10-02T08:10:00Z",
        "temp_dry": 12.5,
        "humidity": 75.0,
    }

    with (
        patch(
            "etl.load.load_observation_once",
            side_effect=psycopg.OperationalError(
                "Database unavailable"
            ),
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
        pytest.raises(psycopg.OperationalError),
    ):
        load_observation(observation)

    assert mock_load.call_count == 6
    assert mock_sleep.call_count == 5