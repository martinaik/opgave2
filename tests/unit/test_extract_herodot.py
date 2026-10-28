# Import necessary modules
from unittest.mock import Mock, patch
import pytest
import requests
from etl.extract_herodot import extract_herodot

@patch("etl.extract_herodot.requests.get")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_success(mock_get):
    """ Tests successful data extraction from the Herodot API. """

    response = Mock()
    response.json.return_value = [
        {"sensor": "temperature", "value": 22.5}
    ]
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = extract_herodot()

    assert result == [{"sensor": "temperature", "value": 22.5}]
    mock_get.assert_called_once_with(
        "https://herodot.spac.dk/api/v1/observations",
        headers={
            "Authorization": "Bearer test-token",
            "Accept": "application/json",
        },
        timeout=30,
    )

@patch.dict("os.environ", {}, clear=True)
def test_extract_herodot_missing_token():
    """ Tests that a ValueError is raised if the HERODOT_API_TOKEN is not set. """

    with pytest.raises(
        ValueError,
        match="HERODOT_API_TOKEN is not set",
    ):
        extract_herodot()

@patch("etl.extract_herodot.requests.get")
@patch("etl.extract_herodot.time.sleep")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_retries_connection_error(mock_sleep, mock_get):
    """ Tests that the function retries on a connection error. """

    response = Mock()
    response.json.return_value = [{"value": 10}]
    response.raise_for_status.return_value = None

    mock_get.side_effect = [
        requests.exceptions.ConnectionError("Connection lost"),
        response,
    ]

    result = extract_herodot()

    assert result == [{"value": 10}]
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

@patch("etl.extract_herodot.requests.get")
@patch("etl.extract_herodot.time.sleep")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_retries_timeout(mock_sleep, mock_get):
    """ Tests that the function retries on a timeout error. """

    response = Mock()
    response.json.return_value = [{"value": 15}]
    response.raise_for_status.return_value = None

    mock_get.side_effect = [
        requests.exceptions.Timeout("Request timed out"),
        response,
    ]

    result = extract_herodot()

    assert result == [{"value": 15}]
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

@pytest.mark.parametrize("status_code", [429, 500, 502, 503])
@patch("etl.extract_herodot.requests.get")
@patch("etl.extract_herodot.time.sleep")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_retries_temporary_http_errors(mock_sleep, mock_get, status_code):
    """ Tests that the function retries on temporary HTTP errors. """

    response = Mock()
    response.status_code = status_code

    error_response = Mock()
    error_response.status_code = status_code

    http_error = requests.exceptions.HTTPError(
        f"HTTP {status_code}",
        response=error_response,
    )

    success_response = Mock()
    success_response.json.return_value = [{"value": 20}]
    success_response.raise_for_status.return_value = None

    mock_get.side_effect = [http_error, success_response]

    result = extract_herodot()

    assert result == [{"value": 20}]
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(5)

@patch("etl.extract_herodot.requests.get")
@patch("etl.extract_herodot.time.sleep")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_does_not_retry_permanent_http_error(mock_sleep, mock_get):
    """ Tests that the function does not retry on a permanent HTTP error. """

    error_response = Mock()
    error_response.status_code = 401

    http_error = requests.exceptions.HTTPError(
        "401 Unauthorized",
        response=error_response,
    )

    mock_get.return_value.raise_for_status.side_effect = http_error

    with pytest.raises(requests.exceptions.HTTPError):
        extract_herodot()

    mock_get.assert_called_once()
    mock_sleep.assert_not_called()

@patch("etl.extract_herodot.requests.get")
@patch("etl.extract_herodot.time.sleep")
@patch.dict("os.environ", {"HERODOT_API_TOKEN": "test-token"})
def test_extract_herodot_raises_after_all_retries(mock_sleep, mock_get):
    """ Tests that the function raises RuntimeError after all retries fail. """
    
    mock_get.side_effect = requests.exceptions.Timeout("Timed out")

    with pytest.raises(
        RuntimeError,
        match="Could not fetch data from Herodot after 5 attempts",
    ):
        extract_herodot()

    assert mock_get.call_count == 5
    assert mock_sleep.call_count == 4
    assert [c.args[0] for c in mock_sleep.call_args_list] == [
        5,
        10,
        15,
        20,
    ]
