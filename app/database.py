# Import necessary modules
import logging
import os
import time
import psycopg

# Set up logging
logger = logging.getLogger(__name__)

# Maximum number of connection attempts
MAX_RETRIES = 6

# Initial delay between retries in seconds
RETRY_DELAY = 5

def get_connection() -> psycopg.Connection:
    """
    Connects to the PostgreSQL database.

    Retries the connection if a temporary database error occurs.
    Returns a connection object.
    """

    # Get the database settings from the environment variables
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return psycopg.connect(
                host=os.environ["POSTGRES_HOST"],
                port=os.environ["POSTGRES_PORT"],
                dbname=os.environ["POSTGRES_DB"],
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASSWORD"],
                connect_timeout=10,
            )

        # Handle temporary connection errors
        except (psycopg.OperationalError, psycopg.InterfaceError):
            logger.exception(
                "Database connection failed "
                "(attempt %s/%s).",
                attempt,
                MAX_RETRIES,
            )

            # If this was the last attempt, raise the exception
            if attempt == MAX_RETRIES:
                raise

            # Calculate the delay before the next attempt
            delay = RETRY_DELAY * attempt

            # Log the retry attempt and wait before trying again
            logger.info(
                "Retrying database connection in %s seconds.",
                delay,
            )

            # Wait for the specified delay before the next attempt
            time.sleep(delay)

def create_source(name: str) -> int:
    """
    Creates a source if it does not already exist.
    Returns the source ID.
    """

    # Connect to the database 
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Add the source if it does not already exist
            cur.execute(
                """
                INSERT INTO source (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING source_id
                """,
                (name,),
            )

            # Get the result of the insert operation
            result = cur.fetchone()

            # Return the new source ID if the insert was successful
            if result:
                return result[0]

            # If the source already exists, find its ID
            cur.execute(
                """
                SELECT source_id
                FROM source
                WHERE name = %s
                """,
                (name,),
            )

            # Get the result of the select operation
            result = cur.fetchone()

            # If the source does not exist, raise an error
            if result is None:
                raise RuntimeError(
                    f"Could not find source '{name}' in the database."
                )

            # Return the existing source ID
            return result[0]
