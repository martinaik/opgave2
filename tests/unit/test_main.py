# Import necessary modules
from unittest.mock import patch
from app.main import main

def test_main() -> None:
    """ Tests the main function. """

    with patch(
        "app.main.run_dmi_etl"
    ) as mock_run_dmi_etl, \
         patch(
             "app.main.time.sleep",
             side_effect=KeyboardInterrupt
         ):

        try:
            main()
        except KeyboardInterrupt:
            pass

    mock_run_dmi_etl.assert_called_once()