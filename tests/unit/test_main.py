from unittest.mock import patch
from app.main import main

def test_main():
    with patch("app.main.create_tables") as mock_create_tables, \
         patch("app.main.run_dmi_etl") as mock_run_dmi_etl:

        main()

    mock_create_tables.assert_called_once()
    mock_run_dmi_etl.assert_called_once()