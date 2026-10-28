# Import necessary modules
from unittest.mock import call, patch
import pytest
from etl.etl_herodot import run_herodot_etl

# Create a fixture to mock the ETL functions
@pytest.fixture
def mocks():
    with (
        patch("etl.etl_herodot.create_source", return_value=2) as source,
        patch("etl.etl_herodot.extract_herodot") as extract,
        patch("etl.etl_herodot.save_batch", return_value=10) as save,
        patch("etl.etl_herodot.get_pending_batches", return_value=[]) as pending,
        patch("etl.etl_herodot.update_batch_status") as status,
        patch(
            "etl.etl_herodot.transform_herodot_observations",
            return_value=[],
        ) as transform,
        patch("etl.etl_herodot.load_herodot_observation") as load,
    ):
        yield {
            "source": source,
            "extract": extract,
            "save": save,
            "pending": pending,
            "status": status,
            "transform": transform,
            "load": load,
        }

def test_run_herodot_etl_extracts_and_stages_data(mocks):
    """ Tests that the ETL process extracts and stages data correctly. """

    mocks["extract"].return_value = {"observations": [{"value": 20}]}

    run_herodot_etl()

    mocks["source"].assert_called_once_with("Herodot")
    mocks["extract"].assert_called_once_with()
    mocks["save"].assert_called_once_with(
        2, {"observations": [{"value": 20}]}
    )
    mocks["pending"].assert_called_once_with()

def test_run_herodot_etl_processes_list_batch(mocks):
    """ Tests that a batch with a list of observations is processed correctly. """

    batch = {
        "batch_id": 11,
        "source_id": 2,
        "raw_data": [{"value": 20}],
    }
    observation = {"temperature": 20}

    mocks["extract"].side_effect = RuntimeError("API unavailable")
    mocks["pending"].return_value = [batch]
    mocks["transform"].return_value = [observation]

    run_herodot_etl()

    mocks["transform"].assert_called_once_with([{"value": 20}], 2)
    mocks["load"].assert_called_once_with(observation)
    assert mocks["status"].call_args_list == [
        call(11, "processing"),
        call(11, "completed"),
    ]

def test_run_herodot_etl_processes_dictionary_batch(mocks):
    """ Tests that a batch with a dictionary of observations is processed correctly. """

    batch = {
        "batch_id": 12,
        "source_id": 2,
        "raw_data": {"observations": [{"value": 25}]},
    }
    mocks["extract"].side_effect = RuntimeError("API unavailable")
    mocks["pending"].return_value = [batch]

    run_herodot_etl()

    mocks["transform"].assert_called_once_with([{"value": 25}], 2)
    mocks["status"].assert_any_call(12, "completed")

def test_run_herodot_etl_ignores_other_sources(mocks):
    """ Tests that batches from other sources are ignored. """

    mocks["pending"].return_value = [
        {
            "batch_id": 13,
            "source_id": 99,
            "raw_data": [],
        }
    ]

    run_herodot_etl()

    mocks["transform"].assert_not_called()
    mocks["load"].assert_not_called()
    mocks["status"].assert_not_called()

def test_run_herodot_etl_marks_batch_failed_when_transform_fails(mocks):
    """ Tests that a batch is marked as failed if transformation fails. """

    batch = {
        "batch_id": 14,
        "source_id": 2,
        "raw_data": [],
    }
    mocks["extract"].side_effect = RuntimeError("API unavailable")
    mocks["pending"].return_value = [batch]
    mocks["transform"].side_effect = ValueError("Invalid observations")

    run_herodot_etl()

    assert mocks["status"].call_args_list == [
        call(14, "processing"),
        call(14, "failed", "Invalid observations"),
    ]
    mocks["load"].assert_not_called()

def test_run_herodot_etl_marks_invalid_batch_failed(mocks):
    """ Tests that a batch with an invalid format is marked as failed. """

    batch = {
        "batch_id": 15,
        "source_id": 2,
        "raw_data": "invalid format",
    }
    mocks["extract"].side_effect = RuntimeError("API unavailable")
    mocks["pending"].return_value = [batch]

    run_herodot_etl()

    mocks["transform"].assert_not_called()
    mocks["status"].assert_any_call(
        15,
        "failed",
        "Unexpected Herodot data format in staging.",
    )

def test_run_herodot_etl_marks_batch_failed_when_load_fails(mocks):
    """ Tests that a batch is marked as failed if loading fails. """
    
    batch = {
        "batch_id": 16,
        "source_id": 2,
        "raw_data": [{"value": 20}],
    }
    mocks["extract"].side_effect = RuntimeError("API unavailable")
    mocks["pending"].return_value = [batch]
    mocks["transform"].return_value = [{"temperature": 20}]
    mocks["load"].side_effect = RuntimeError("Database unavailable")

    run_herodot_etl()

    assert mocks["status"].call_args_list == [
        call(16, "processing"),
        call(16, "failed", "Database unavailable"),
    ]
