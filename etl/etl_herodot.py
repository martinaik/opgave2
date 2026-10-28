# Import necessary modules
import logging
from app.database import create_source
from etl.extract_herodot import extract_herodot
from etl.transform import transform_herodot_observations
from etl.load import load_herodot_observation
from etl.staging import (save_batch, get_pending_batches, update_batch_status)

# Set up logging
logger = logging.getLogger(__name__)

def run_herodot_etl() -> None:
    """ Extracts, stages, transforms, and loads data from the Herodot API into the database. """

    # Log the start of the ETL process
    logger.info("Starting Herodot ETL process.")

    # Get the source ID for Herodot
    source_id = create_source("Herodot")

    # Try to fetch and stage new data
    # If this fails, continue with batches already in staging
    try:
        data = extract_herodot()

        batch_id = save_batch(source_id, data)

        logger.info(
            "Saved raw Herodot data in staging batch %s.",
            batch_id,
        )

    # Handle any exceptions that occur during the extraction and staging of new data
    except Exception:
        logger.exception(
            "Could not fetch and stage new Herodot data. "
            "Will attempt to process existing staging batches."
        )

    # Process pending, failed or interrupted batches
    for batch in get_pending_batches():

        # Only process batches belonging to Herodot
        if batch["source_id"] != source_id:
            continue

        # Get the batch ID for logging and processing
        batch_id = batch["batch_id"]

        try:
            # Mark batch as being processed
            update_batch_status(batch_id, "processing")

            # Get the raw data from staging
            raw_data = batch["raw_data"]

            # Handle a response that is a list or a dictionary
            if isinstance(raw_data, dict):
                raw_observations = raw_data.get("observations", [])
            elif isinstance(raw_data, list):
                raw_observations = raw_data
            else:
                raise ValueError(
                    "Unexpected Herodot data format in staging."
                )

            # Transform the raw data
            observations = transform_herodot_observations(
                raw_observations,
                batch["source_id"],
            )

            # Load the transformed data
            for observation in observations:
                load_herodot_observation(observation)

            # Mark batch as completed
            update_batch_status(batch_id, "completed")

            # Log that the staging batch has been completed
            logger.info(
                "Herodot staging batch %s completed. "
                "%s observations processed.",
                batch_id,
                len(observations),
            )

        # Handle any exceptions that occur during the processing of the staging batch
        except Exception as exc:
            logger.exception(
                "Failed to process Herodot staging batch %s.",
                batch_id,
            )

            update_batch_status(
                batch_id,
                "failed",
                str(exc),
            )
