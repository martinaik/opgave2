# Import necessary modules
import logging
import time
import requests

# URL for the DMI API
url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

# API parameters
PARAMS = {
    "period": "latest-10-minutes",
    "limit": 1000,
}

# Set up logging
logger = logging.getLogger(__name__)

# Maximum number of request attempts
MAX_RETRIES = 5

# Initial delay between retries in seconds
RETRY_DELAY = 5

def extract_dmi() -> dict:
    """
    Extract data from the DMI API.

    Retries the request after temporary connection errors,
    timeouts, HTTP 429 errors, and server errors.

    Returns:
        dict: The JSON response from the DMI API.

    Raises:
        RuntimeError: If the request fails after all attempts.
        requests.exceptions.HTTPError: If a permanent HTTP error occurs.
    """

    # Attempt to fetch data from the DMI API with retries
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Make a GET request to the DMI API with a timeout
            response = requests.get( 
                url,
                params=PARAMS,
                timeout=30,
            )

            # Check if the request was successful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Log that the data was successfully fetched from the DMI API
            logger.info("Successfully fetched data from DMI.")

            return data

        # Handle temporary connection errors and timeouts
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as error:
            logger.warning(
                "DMI connection failed (attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        # Handle HTTP errors, including rate limiting and server errors
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code

            # Retry only rate-limit and server errors.
            if status_code != 429 and status_code < 500:
                logger.error(
                    "Permanent HTTP error from DMI: %s",
                    status_code,
                )
                raise

            # Log the temporary HTTP error and retry
            logger.warning(
                "Temporary HTTP error from DMI "
                "(attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        if attempt < MAX_RETRIES:
            delay = RETRY_DELAY * attempt

            # Log the retry attempt and wait before trying again
            logger.info(
                "Retrying DMI request in %s seconds.",
                delay,
            )

            # Wait for the specified delay before the next attempt
            time.sleep(delay)

    # If all attempts fail, raise a RuntimeError
    raise RuntimeError(
        f"Could not fetch data from DMI after {MAX_RETRIES} attempts."
    )

