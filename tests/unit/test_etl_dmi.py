# Import necessary modules
from unittest.mock import patch
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
                    "observed": "2026-10-02T08:10:00Z",
                },
                "geometry": {
                    "coordinates": [9.5, 55.7],
                },
            },
            {
                "properties": {
                    "stationId": "06110",
                    "parameterId": "humidity",
                    "value": 75.0,
                    "observed": "2026-10-02T08:10:00Z",
                },
                "geometry": {
                    "coordinates": [9.5, 55.7],
                },
            },
        ]
    }

    fake_batch = {
        "batch_id": 10,
        "source_id": 1,
        "raw_data": fake_data["features"],
        "status": "pending",
    }

    with (
        patch(
            "etl.etl_dmi.create_source",
            return_value=1,
        ),
        patch(
            "etl.etl_dmi.extract_dmi",
            return_value=fake_data,
        ),
        patch(
            "etl.etl_dmi.save_batch",
            return_value=10,
        ) as mock_save_batch,
        patch(
            "etl.etl_dmi.get_pending_batches",
            return_value=[fake_batch],
        ),
        patch("etl.etl_dmi.update_batch_status") as mock_status,
        patch(
            "etl.etl_dmi.transform_observations",
            return_value=[
                {"station_id": "06110", "humidity": 75.0}
            ],
        ) as mock_transform,
        patch("etl.etl_dmi.load_observation") as mock_load,
    ):
        run_dmi_etl()

    mock_save_batch.assert_called_once_with(
        1,
        fake_data["features"],
    )
    mock_transform.assert_called_once_with(
        fake_data["features"],
        1,
    )
    mock_load.assert_called_once_with(
        {"station_id": "06110", "humidity": 75.0}
    )
    assert mock_status.call_count == 2
    mock_status.assert_any_call(10, "processing")
    mock_status.assert_any_call(10, "completed")

def test_run_dmi_etl_marks_batch_as_failed() -> None:
    """ Tests that a batch is marked as failed if transformation fails. """

    fake_data = {
        "features": [{"properties": {}, "geometry": {}}]
    }

    fake_batch = {
        "batch_id": 10,
        "source_id": 1,
        "raw_data": fake_data["features"],
        "status": "pending",
    }

    with (
        patch("etl.etl_dmi.create_source", return_value=1),
        patch("etl.etl_dmi.extract_dmi", return_value=fake_data),
        patch("etl.etl_dmi.save_batch", return_value=10),
        patch("etl.etl_dmi.get_pending_batches", return_value=[fake_batch]),
        patch("etl.etl_dmi.update_batch_status") as mock_status,
        patch(
            "etl.etl_dmi.transform_observations",
            side_effect=ValueError("Invalid observation"),
        ),
        patch("etl.etl_dmi.load_observation"),
    ):
        run_dmi_etl()

    mock_status.assert_any_call(10, "processing")
    mock_status.assert_any_call(
        10, "failed", "Invalid observation"
    )
