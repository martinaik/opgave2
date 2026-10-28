# Import necessary modules
import psycopg
import pytest
from unittest.mock import MagicMock, patch
from etl.load import (load_observation, load_herodot_observation, load_herodot_observation_once)

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
    
def make_herodot_observation() -> dict:
    """ Creates a sample transformed Herodot observation. """

    return {
        "node_id": "node-1",
        "instrument_id": "SCD41:123",
        "instrument_model": "SCD41",
        "source_id": 2,
        "observed": "2026-10-02T08:10:00+00:00",
        "temperature": 22.5,
        "co2_concentration": 650,
        "humidity": 55.0,
        "pressure": 1013.25,
    }

def test_load_herodot_observation_once() -> None:
    """ Tests that a Herodot observation is inserted into the database. """

    observation = make_herodot_observation()

    mock_cursor = MagicMock()
    mock_cursor_context = MagicMock()
    mock_cursor_context.__enter__.return_value = mock_cursor

    mock_connection = MagicMock()
    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value = mock_cursor_context

    mock_connection_context = MagicMock()
    mock_connection_context.__enter__.return_value = mock_connection

    with patch(
        "etl.load.get_connection",
        return_value=mock_connection_context,
    ):
        load_herodot_observation_once(observation)

    mock_cursor.execute.assert_called_once()

    sql = mock_cursor.execute.call_args[0][0]
    assert "INSERT INTO herodot_measurement" in sql
    assert "ON CONFLICT" in sql

    values = mock_cursor.execute.call_args[0][1]
    assert values[0] == "node-1"
    assert values[1] == "SCD41:123"
    assert values[3] == 2

def test_load_herodot_observation_retries_after_database_error() -> None:
    """ Tests retrying after a temporary database error. """

    observation = make_herodot_observation()

    with (
        patch(
            "etl.load.load_herodot_observation_once",
            side_effect=[
                psycopg.OperationalError("Temporary failure"),
                None,
            ],
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
    ):
        load_herodot_observation(observation)

    assert mock_load.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_load_herodot_observation_retries_after_interface_error() -> None:
    """ Tests retrying after a database interface error. """

    observation = make_herodot_observation()

    with (
        patch(
            "etl.load.load_herodot_observation_once",
            side_effect=[
                psycopg.InterfaceError("Connection lost"),
                None,
            ],
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
    ):
        load_herodot_observation(observation)

    assert mock_load.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_load_herodot_observation_fails_after_max_retries() -> None:
    """ Tests raising an error when all retry attempts fail. """

    observation = make_herodot_observation()

    with (
        patch(
            "etl.load.load_herodot_observation_once",
            side_effect=psycopg.OperationalError("Database unavailable"),
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
        pytest.raises(psycopg.OperationalError),
    ):
        load_herodot_observation(observation)

    assert mock_load.call_count == 6
    assert mock_sleep.call_count == 5

def test_load_observation_retries_after_interface_error() -> None:
    """ Tests retrying after a database interface error. """

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
                psycopg.InterfaceError("Connection lost"),
                None,
            ],
        ) as mock_load,
        patch("etl.load.time.sleep") as mock_sleep,
    ):
        load_observation(observation)

    assert mock_load.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_load_observation_uses_increasing_retry_delays() -> None:
    """ Tests that retry delays increase after each failure. """
    
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
            side_effect=psycopg.OperationalError("Temporary failure"),
        ),
        patch("etl.load.time.sleep") as mock_sleep,
        pytest.raises(psycopg.OperationalError),
    ):
        load_observation(observation)

    assert [call.args[0] for call in mock_sleep.call_args_list] == [
        5, 10, 15, 20, 25
    ]
