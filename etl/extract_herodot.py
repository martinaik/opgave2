# Import necessary modules
import logging
import time
import requests
import os

# URL for the Herodot API
url = "https://herodot.spac.dk/api/v1/observations"

# Set up logging
logger = logging.getLogger(__name__)

# Maximum number of request attempts
MAX_RETRIES = 5

# Initial delay between retries in seconds
RETRY_DELAY = 5

def extract_herodot() -> list[dict]:
    """
    Extracts data from the Herodot API.

    Retries the request after temporary connection errors,
    timeouts, HTTP 429 errors, and server errors.

    Returns:
        list[dict]: The JSON response from the Herodot API.

    Raises:
        RuntimeError: If the request fails after all attempts.
        requests.exceptions.HTTPError: If a permanent HTTP error occurs.
    """

    # Get the Herodot API token from the environment variable
    token = os.getenv("HERODOT_API_TOKEN")

    # Raise an error if the token is not set
    if not token:
        raise ValueError("HERODOT_API_TOKEN is not set.")

    # Headers used to authenticate with the Herodot API
    headers = {
        "Authorization": f"Bearer {token.strip()}",
        "Accept": "application/json",
    }

    # Attempt to fetch data from the Herodot API with retries
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Make a GET request to the Herodot API
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
            )

            # Check if the request was successful
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Log successful extraction
            logger.info("Successfully fetched data from Herodot.")

            return data

        # Handle temporary connection errors and timeouts
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        ) as error:
            logger.warning(
                "Herodot connection failed (attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        # Handle HTTP errors, including rate limiting and server errors
        except requests.exceptions.HTTPError as error:
            status_code = error.response.status_code

            # Retry only rate-limit and server errors
            if status_code != 429 and status_code < 500:
                logger.error(
                    "Permanent HTTP error from Herodot: %s",
                    status_code,
                )
                raise

            logger.warning(
                "Temporary HTTP error from Herodot "
                "(attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

        # If this was not the last attempt, wait before retrying
        if attempt < MAX_RETRIES:
            delay = RETRY_DELAY * attempt

            # Log the retry attempt and wait before trying again
            logger.info(
                "Retrying Herodot request in %s seconds.",
                delay,
            )

            # Wait for the specified delay before the next attempt
            time.sleep(delay)

    # If all attempts fail, raise an error
    raise RuntimeError(
        f"Could not fetch data from Herodot after {MAX_RETRIES} attempts."
    )
