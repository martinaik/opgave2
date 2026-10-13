# Import necessary modules
import pytest
import requests
from unittest.mock import MagicMock, patch
from etl.extract_dmi import extract_dmi

def test_extract_dmi() -> None:
    """ Tests that data is extracted from the DMI API. """

    fake_response = MagicMock()
    fake_response.json.return_value = {"features": []}

    with patch(
        "etl.extract_dmi.requests.get",
        return_value=fake_response,
    ) as mock_get:
        result = extract_dmi()

    fake_response.raise_for_status.assert_called_once()
    mock_get.assert_called_once()
    assert result == {"features": []}

def test_extract_dmi_retries_after_connection_error() -> None:
    """ Tests retrying after a temporary connection error. """

    fake_response = MagicMock()
    fake_response.json.return_value = {"features": []}

    with (
        patch(
            "etl.extract_dmi.requests.get",
            side_effect=[
                requests.exceptions.ConnectionError(
                    "Temporary connection error"
                ),
                fake_response,
            ],
        ) as mock_get,
        patch("etl.extract_dmi.time.sleep") as mock_sleep,
    ):
        result = extract_dmi()

    assert result == {"features": []}
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_extract_dmi_retries_after_timeout() -> None:
    """ Tests retrying after a request timeout. """

    fake_response = MagicMock()
    fake_response.json.return_value = {"features": []}

    with (
        patch(
            "etl.extract_dmi.requests.get",
            side_effect=[
                requests.exceptions.Timeout("Request timed out"),
                fake_response,
            ],
        ) as mock_get,
        patch("etl.extract_dmi.time.sleep") as mock_sleep,
    ):
        result = extract_dmi()

    assert result == {"features": []}
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_extract_dmi_retries_after_temporary_http_error(status_code: int) -> None:
    """ Tests retrying after rate-limit and server errors. """

    fake_response = MagicMock()
    fake_response.status_code = status_code
    fake_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(
            f"HTTP {status_code}",
            response=fake_response,
        )
    )

    successful_response = MagicMock()
    successful_response.json.return_value = {"features": []}

    with (
        patch(
            "etl.extract_dmi.requests.get",
            side_effect=[fake_response, successful_response],
        ) as mock_get,
        patch("etl.extract_dmi.time.sleep") as mock_sleep,
    ):
        result = extract_dmi()

    assert result == {"features": []}
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

def test_extract_dmi_does_not_retry_permanent_http_error() -> None:
    """ Tests that a permanent HTTP error is raised immediately. """

    fake_response = MagicMock()
    fake_response.status_code = 404
    fake_response.raise_for_status.side_effect = (
        requests.exceptions.HTTPError(
            "HTTP 404",
            response=fake_response,
        )
    )

    with (
        patch(
            "etl.extract_dmi.requests.get",
            return_value=fake_response,
        ) as mock_get,
        patch("etl.extract_dmi.time.sleep") as mock_sleep,
        pytest.raises(requests.exceptions.HTTPError),
    ):
        extract_dmi()

    mock_get.assert_called_once()
    mock_sleep.assert_not_called()

def test_extract_dmi_fails_after_max_retries() -> None:
    """ Tests raising an error after all retry attempts fail. """

    with (
        patch(
            "etl.extract_dmi.requests.get",
            side_effect=requests.exceptions.ConnectionError(
                "DMI API unavailable"
            ),
        ) as mock_get,
        patch("etl.extract_dmi.time.sleep") as mock_sleep,
        pytest.raises(
            RuntimeError,
            match="Could not fetch data from DMI",
        ),
    ):
        extract_dmi()

    assert mock_get.call_count == 5
    assert mock_sleep.call_count == 4