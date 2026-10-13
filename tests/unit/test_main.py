# Import necessary modules
from unittest.mock import patch
from app.main import main

def test_main_runs_migrations_and_etl() -> None:
    """ Tests that migrations run before the ETL process. """

    call_order = []

    with (
        patch(
            "app.main.run_migrations",
            side_effect=lambda: call_order.append("migrations"),
        ),
        patch(
            "app.main.run_dmi_etl",
            side_effect=lambda: call_order.append("etl"),
        ),
        patch(
            "app.main.time.sleep",
            side_effect=KeyboardInterrupt,
        ),
    ):
        try:
            main()
        except KeyboardInterrupt:
            pass

    assert call_order == ["migrations", "etl"]

def test_main_retries_after_etl_failure() -> None:
    """ Tests that the program retries after an ETL failure. """

    with (
        patch("app.main.run_migrations") as mock_migrations,
        patch(
            "app.main.run_dmi_etl",
            side_effect=[Exception("ETL failed"), None],
        ) as mock_etl,
        patch(
            "app.main.time.sleep",
            side_effect=[None, KeyboardInterrupt],
        ) as mock_sleep,
    ):
        try:
            main()
        except KeyboardInterrupt:
            pass

    assert mock_migrations.call_count == 2
    assert mock_etl.call_count == 2
    assert mock_sleep.call_count == 2

def test_main_waits_10_minutes() -> None:
    """ Tests that the program waits 600 seconds between cycles. """

    with (
        patch("app.main.run_migrations"),
        patch("app.main.run_dmi_etl"),
        patch(
            "app.main.time.sleep",
            side_effect=KeyboardInterrupt,
        ) as mock_sleep,
    ):
        try:
            main()
        except KeyboardInterrupt:
            pass

    mock_sleep.assert_called_once_with(600)
