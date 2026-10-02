from unittest.mock import MagicMock, patch
from etl.extract_dmi import run_dmi_etl

def test_run_dmi_etl():
    fake_response = MagicMock()

    fake_response.json.return_value = {
        "features": [
            {
                "properties": {
                    "stationId": "06110",
                    "parameterId": "temp_dry",
                    "value": 12.5,
                    "observed": "2026-10-02T08:10:00Z"
                },
                "geometry": {
                    "coordinates": [9.5, 55.7]
                }
            }
        ]
    }

    with patch("etl.extract_dmi.create_source", return_value=1), \
         patch("etl.extract_dmi.requests.get", return_value=fake_response), \
         patch("etl.extract_dmi.load_observation") as mock_load:

        run_dmi_etl()

    fake_response.raise_for_status.assert_called_once()
    mock_load.assert_called_once()