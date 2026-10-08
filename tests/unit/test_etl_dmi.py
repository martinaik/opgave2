# Import necessary modules
from unittest.mock import MagicMock, patch
from etl.etl_dmi import run_dmi_etl

def test_run_dmi_etl() -> None:
    """ Tests the complete DMI ETL process. """

    fake_data = {
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
            },
            {
                "properties": {
                    "stationId": "06110",
                    "parameterId": "humidity",
                    "value": 75.0,
                    "observed": "2026-10-02T08:10:00Z"
                },
                "geometry": {
                    "coordinates": [9.5, 55.7]
                }
            }
        ]
    }

    with patch(
        "etl.etl_dmi.create_source",
        return_value=1
    ), patch(
        "etl.etl_dmi.extract_dmi",
        return_value=fake_data
    ), patch(
        "etl.etl_dmi.transform_observations",
        return_value=[
            {"station_id": "06110", "humidity": 75.0}
        ]
    ) as mock_transform, patch(
        "etl.etl_dmi.load_observation"
    ) as mock_load:

        run_dmi_etl()

    mock_transform.assert_called_once()
    mock_load.assert_called_once()