# Import necessary modules
from unittest.mock import MagicMock, patch
from etl.extract_dmi import extract_dmi

def test_extract_dmi() -> None:
    """ Tests that data is extracted from the DMI API. """

    fake_response = MagicMock()

    fake_response.json.return_value = {
        "features": []
    }

    with patch(
        "etl.extract_dmi.requests.get",
        return_value=fake_response
    ):
        result = extract_dmi()

    fake_response.raise_for_status.assert_called_once()
    assert result == {"features": []}