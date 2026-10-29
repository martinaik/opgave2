# Import necessary modules
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.api import app

# Create a TestClient instance for the FastAPI app
client = TestClient(app)

def setup_database_mock(mock_get_connection):
    """ Sets up a mock database connection and cursor. """
    
    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_get_connection.return_value.__enter__.return_value = (
        mock_connection
    )
    mock_connection.cursor.return_value.__enter__.return_value = (
        mock_cursor
    )

    return mock_cursor

def test_root():
    """ Tests the welcome endpoint. """

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the Environmental Data API!"
    }

def test_health_check():
    """ Tests the health endpoint. """

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.api.get_connection")
def test_get_stations(mock_get_connection):
    """ Tests retrieving all stations. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchall.return_value = [
        ("06058", 55.7, 12.5),
        ("06108", 55.9, 12.3),
    ]

    response = client.get("/dmi/stations")

    assert response.status_code == 200
    assert response.json() == [
        {
            "station_id": "06058",
            "latitude": 55.7,
            "longitude": 12.5,
        },
        {
            "station_id": "06108",
            "latitude": 55.9,
            "longitude": 12.3,
        },
    ]
    mock_cursor.execute.assert_called_once()

@patch("app.api.get_connection")
def test_get_stations_empty(mock_get_connection):
    """ Tests retrieving stations when none exist. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchall.return_value = []

    response = client.get("/dmi/stations")

    assert response.status_code == 200
    assert response.json() == []

@patch("app.api.get_connection")
def test_get_stations_database_error(mock_get_connection):
    """ Tests that a database error returns HTTP 500. """

    mock_get_connection.side_effect = Exception(
        "Database unavailable"
    )

    response = client.get("/dmi/stations")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve stations from the database."
    )

@patch("app.api.get_connection")
def test_get_station(mock_get_connection):
    """ Tests retrieving one station by ID. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchone.return_value = ("06058", 55.7, 12.5)

    response = client.get("/dmi/stations/06058")

    assert response.status_code == 200
    assert response.json() == {
        "station_id": "06058",
        "latitude": 55.7,
        "longitude": 12.5,
    }
    mock_cursor.execute.assert_called_once()

@patch("app.api.get_connection")
def test_get_station_not_found(mock_get_connection):
    """ Tests that a missing station returns HTTP 404. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchone.return_value = None

    response = client.get("/dmi/stations/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Station not found."}

@patch("app.api.get_connection")
def test_get_station_database_error(mock_get_connection):
    """ Tests that a database error returns HTTP 500. """

    mock_get_connection.side_effect = Exception(
        "Database unavailable"
    )

    response = client.get("/dmi/stations/06058")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve station from the database."
    )

@patch("app.api.get_connection")
def test_get_sources(mock_get_connection):
    """ Tests retrieving all data sources. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchall.return_value = [
        (1, "DMI"),
        (2, "Other source"),
    ]

    response = client.get("/sources")

    assert response.status_code == 200
    assert response.json() == [
        {"source_id": 1, "name": "DMI"},
        {"source_id": 2, "name": "Other source"},
    ]

@patch("app.api.get_connection")
def test_get_sources_empty(mock_get_connection):
    """ Tests retrieving sources when none exist. """

    mock_cursor = setup_database_mock(mock_get_connection)
    mock_cursor.fetchall.return_value = []

    response = client.get("/sources")

    assert response.status_code == 200
    assert response.json() == []

@patch("app.api.get_connection")
def test_get_sources_database_error(mock_get_connection):
    """ Tests that a database error returns HTTP 500. """

    mock_get_connection.side_effect = Exception(
        "Database unavailable"
    )

    response = client.get("/sources")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve data sources from the database."
    )

def setup_combined_measurement_mock(mock_get_connection):
    """ Sets up a mock for combined DMI and Herodot measurements. """

    mock_cursor = setup_database_mock(mock_get_connection)

    mock_cursor.description = [
        SimpleNamespace(name="data_source"),
        SimpleNamespace(name="source_id"),
        SimpleNamespace(name="observed"),
        SimpleNamespace(name="measurement_data"),
    ]

    mock_cursor.fetchall.return_value = [
        (
            "DMI",
            1,
            datetime(2026, 10, 1, 12, 0),
            {"station_id": "06058", "temp_dry": 15.5},
        ),
        (
            "Herodot",
            2,
            datetime(2026, 10, 1, 12, 10),
            {"temperature": 22.5, "co2_concentration": 600},
        ),
    ]

    return mock_cursor

@patch("app.api.get_connection")
def test_get_combined_measurements(mock_get_connection):
    """ Tests retrieving measurements from DMI and Herodot. """

    mock_cursor = setup_combined_measurement_mock(mock_get_connection)

    response = client.get("/measurements")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 2
    assert data[0]["data_source"] == "DMI"
    assert data[0]["measurement_data"]["station_id"] == "06058"
    assert data[1]["data_source"] == "Herodot"
    assert data[1]["measurement_data"]["temperature"] == 22.5

    mock_cursor.execute.assert_called_once()

@patch("app.api.get_connection")
def test_get_combined_measurements_with_filters(mock_get_connection):
    """ Tests filtering combined measurements by source and time. """

    mock_cursor = setup_combined_measurement_mock(mock_get_connection)

    response = client.get(
        "/measurements",
        params={
            "source_id": 2,
            "start_time": "2026-10-01T00:00:00",
            "end_time": "2026-10-02T00:00:00",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    query, params = mock_cursor.execute.call_args.args

    assert "source_id = %s" in query
    assert "observed >= %s" in query
    assert "observed <= %s" in query
    assert "ORDER BY observed DESC LIMIT %s" in query

    assert params == [
        2,
        datetime(2026, 10, 1, 0, 0),
        datetime(2026, 10, 2, 0, 0),
        10,
    ]

def test_get_combined_measurements_invalid_time_range():
    """ Tests that an invalid time range returns HTTP 400. """

    response = client.get(
        "/measurements",
        params={
            "start_time": "2026-10-02T00:00:00",
            "end_time": "2026-10-01T00:00:00",
        },
    )

    assert response.status_code == 400

def test_get_combined_measurements_limit_too_high():
    """ Tests that a limit above 100 returns HTTP 422. """

    response = client.get("/measurements?limit=101")

    assert response.status_code == 422

@patch("app.api.get_connection")
def test_get_combined_measurements_database_error(mock_get_connection):
    """ Tests that a database error returns HTTP 500. """

    mock_get_connection.side_effect = Exception("Database unavailable")

    response = client.get("/measurements")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve measurements from the database."
    )


def setup_dmi_measurement_mock(mock_get_connection):
    """ Sets up a mock connection with dmi measurement results. """

    mock_cursor = setup_database_mock(mock_get_connection)

    mock_cursor.description = [
        SimpleNamespace(name="station_id"),
        SimpleNamespace(name="observed"),
        SimpleNamespace(name="value"),
    ]

    mock_cursor.fetchall.return_value = [
        ("06058", datetime(2026, 10, 1, 12, 0), 15.5),
    ]

    return mock_cursor

@patch("app.api.get_connection")
def test_get_dmi_measurements(mock_get_connection):
    """ Tests retrieving dmi measurements without filters. """

    mock_cursor = setup_dmi_measurement_mock(mock_get_connection)

    response = client.get("/dmi/measurements")

    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["station_id"] == "06058"
    assert data[0]["observed"] == "2026-10-01T12:00:00" 
    assert data[0]["value"] == 15.5

    mock_cursor.execute.assert_called_once()

@patch("app.api.get_connection")
def test_get_dmi_measurements_with_filters(mock_get_connection):
    """ Tests filtering dmi measurements by station, source and time. """

    mock_cursor = setup_dmi_measurement_mock(mock_get_connection)

    response = client.get(
        "/dmi/measurements",
        params={
            "station_id": "06058",
            "start_time": "2026-10-01T00:00:00",
            "end_time": "2026-10-02T00:00:00",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    mock_cursor.execute.assert_called_once()
    query, params = mock_cursor.execute.call_args.args

    assert "station_id = %s" in query
    assert "observed >= %s" in query
    assert "observed <= %s" in query
    assert "ORDER BY observed DESC LIMIT %s" in query

    assert params == [
        "06058",
        datetime(2026, 10, 1, 0, 0),
        datetime(2026, 10, 2, 0, 0),
        10,
    ]

def test_get_dmi_measurements_invalid_time_range():
    """ Tests that start_time after end_time returns HTTP 400. """

    response = client.get(
        "/dmi/measurements",
        params={
            "start_time": "2026-10-02T00:00:00",
            "end_time": "2026-10-01T00:00:00",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "start_time must be before or equal to end_time."
    )

def test_get_dmi_measurements_limit_too_high():
    """ Tests that a limit above 100 returns HTTP 422. """

    response = client.get("/dmi/measurements?limit=101")

    assert response.status_code == 422

def test_get_dmi_measurements_limit_too_low():
    """ Tests that a limit below 1 returns HTTP 422. """

    response = client.get("/dmi/measurements?limit=0")

    assert response.status_code == 422

@patch("app.api.get_connection")
def test_get_dmi_measurements_database_error(mock_get_connection):
    """ Tests that a database error returns HTTP 500. """

    mock_get_connection.side_effect = Exception(
        "Database unavailable"
    )

    response = client.get("/dmi/measurements")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve measurements from the database."
    )


def setup_herodot_measurement_mock(mock_get_connection):
    """ Sets up a mock for Herodot measurements. """

    mock_cursor = setup_database_mock(mock_get_connection)

    mock_cursor.description = [
        SimpleNamespace(name="node_id"),
        SimpleNamespace(name="instrument_id"),
        SimpleNamespace(name="instrument_model"),
        SimpleNamespace(name="observed"),
        SimpleNamespace(name="temperature"),
        SimpleNamespace(name="co2_concentration"),
        SimpleNamespace(name="humidity"),
        SimpleNamespace(name="pressure"),
    ]

    mock_cursor.fetchall.return_value = [
        (
            "12345678-1234-1234-1234-123456789abc",
            "sensor-01",
            "Herodot sensor",
            datetime(2026, 10, 1, 12, 0),
            22.5,
            600.0,
            45.0,
            1013.0,
        ),
    ]

    return mock_cursor

@patch("app.api.get_connection")
def test_get_herodot_measurements(mock_get_connection):
    """ Tests retrieving Herodot measurements. """

    mock_cursor = setup_herodot_measurement_mock(mock_get_connection)

    response = client.get("/herodot/measurements")

    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["node_id"] == (
        "12345678-1234-1234-1234-123456789abc"
    )
    assert data[0]["instrument_id"] == "sensor-01"
    assert data[0]["temperature"] == 22.5
    assert data[0]["co2_concentration"] == 600.0

    mock_cursor.execute.assert_called_once()

@patch("app.api.get_connection")
def test_get_herodot_measurements_with_filters(mock_get_connection):
    """ Tests filtering Herodot measurements. """

    mock_cursor = setup_herodot_measurement_mock(mock_get_connection)

    response = client.get(
        "/herodot/measurements",
        params={
            "node_id": "12345678-1234-1234-1234-123456789abc",
            "instrument_id": "sensor-01",
            "instrument_model": "Herodot sensor",
            "start_time": "2026-10-01T00:00:00",
            "end_time": "2026-10-02T00:00:00",
            "limit": 10,
        },
    )

    assert response.status_code == 200

    query, params = mock_cursor.execute.call_args.args

    assert "node_id = %s" in query
    assert "instrument_id = %s" in query
    assert "instrument_model = %s" in query
    assert "observed >= %s" in query
    assert "observed <= %s" in query
    assert "ORDER BY observed DESC LIMIT %s" in query

    assert params == [
        "12345678-1234-1234-1234-123456789abc",
        "sensor-01",
        "Herodot sensor",
        datetime(2026, 10, 1, 0, 0),
        datetime(2026, 10, 2, 0, 0),
        10,
    ]

def test_get_herodot_measurements_invalid_time_range():
    """ Tests that an invalid time range returns HTTP 400. """

    response = client.get(
        "/herodot/measurements",
        params={
            "start_time": "2026-10-02T00:00:00",
            "end_time": "2026-10-01T00:00:00",
        },
    )

    assert response.status_code == 400

def test_get_herodot_measurements_limit_too_high():
    """ Tests that a limit above 100 returns HTTP 422. """
    
    response = client.get("/herodot/measurements?limit=101")

    assert response.status_code == 422

@patch("app.api.get_connection")
def test_get_herodot_measurements_database_error(mock_get_connection):

    """ Tests that a database error returns HTTP 500. """
    mock_get_connection.side_effect = Exception("Database unavailable")

    response = client.get("/herodot/measurements")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Could not retrieve Herodot measurements from the database."
    )
