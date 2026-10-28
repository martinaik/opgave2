# Import necessary modules
import json
from typing import Any
from app.database import get_connection

def save_batch(source_id: int, raw_data: dict | list) -> int:
    """ Saves raw API data as a staging batch and return its ID. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert the raw data into the staging_batch table
            cur.execute(
                """
                INSERT INTO staging_batch (source_id, raw_data)
                VALUES (%s, %s)
                RETURNING batch_id;
                """,
                (source_id, json.dumps(raw_data)),
            )

            # Fetch the newly created batch ID
            batch_id = cur.fetchone()[0]

    return batch_id

def get_pending_batches() -> list[dict[str, Any]]:
    """ Retrieves batches that are pending or have failed. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Query the staging_batch table for batches with status
            cur.execute(
                """
                SELECT batch_id, source_id, raw_data, status
                FROM staging_batch
                WHERE status IN ('pending', 'failed', 'processing')
                ORDER BY batch_id;
                """
            )

            # Fetch all rows that match the query
            rows = cur.fetchall()

    # Return a list of dictionaries representing the pending batches
    return [
        {
            "batch_id": row[0],
            "source_id": row[1],
            "raw_data": row[2],
            "status": row[3],
        }
        for row in rows
    ]

def update_batch_status(batch_id: int, status: str, error_message: str | None = None) -> None:
    """ Updates a batch's status and optional error message. """

    # Validate the provided status
    if status not in {"pending", "processing", "failed", "completed"}:
        raise ValueError(f"Invalid staging status: {status}")

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Update the status and error message of the specified batch
            cur.execute(
                """
                UPDATE staging_batch
                SET status = %s,
                    error_message = %s,
                    processed_at = CASE
                        WHEN %s = 'completed' THEN NOW()
                        ELSE NULL
                    END
                WHERE batch_id = %s;
                """,
                (status, error_message, status, batch_id),
            )
