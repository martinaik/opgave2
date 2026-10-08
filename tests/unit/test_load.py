# Import necessary modules
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
        "humidity": 75.0
    }

    mock_cursor = MagicMock()
    mock_connection = MagicMock()

    mock_connection.__enter__.return_value = mock_connection
    mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

    with patch(
        "etl.load.get_connection",
        return_value=mock_connection
    ):
        load_observation(observation)

    assert mock_cursor.execute.call_count == 2