# Import necessary modules
import logging
from app.database import create_source
from etl.extract_dmi import extract_dmi
from etl.transform import transform_observations
from etl.load import load_observation
from etl.staging import save_batch, get_pending_batches, update_batch_status

# Set up logging
logger = logging.getLogger(__name__)

def run_dmi_etl() -> None:
    """ Extracts data from the DMI API, stages it, transforms it, and loads it into the database. """

    # Log the start of the ETL process
    logger.info("Starting DMI ETL process.")

    # Get the source ID for DMI
    source_id = create_source("DMI")

    # Try to fetch and stage new data
    # If this fails, continue with batches already in staging
    try:
        data = extract_dmi()
        batch_id = save_batch(source_id, data["features"])

        logger.info(
            "Saved raw DMI data in staging batch %s.",
            batch_id,
        )

    # Handle any exceptions that occur during the extraction and staging of new data
    except Exception:
        logger.exception(
            "Could not fetch and stage new DMI data. "
            "Will attempt to process existing staging batches."
        )

    # Process batches already saved in staging.
    for batch in get_pending_batches():
        # Only process batches belonging to DMI
        if batch["source_id"] != source_id:
            continue

        # Get the batch ID for logging and processing
        current_batch_id = batch["batch_id"]

        try:
            # Mark the batch as being processed
            update_batch_status(current_batch_id, "processing")

            # Transform the raw data
            observations = transform_observations(
                batch["raw_data"],
                batch["source_id"],
            )

            # Load observations into the database
            for observation in observations:
                load_observation(observation)

            # Mark the batch as completed
            update_batch_status(current_batch_id, "completed")

            # Log that the staging batch has been completed
            logger.info(
                "Staging batch %s completed. %s observations processed.",
                current_batch_id,
                len(observations),
            )

        # Handle any exceptions that occur during the processing of the staging batch
        except Exception as exc:
            logger.exception(
                "Failed to process staging batch %s.",
                current_batch_id,
            )

            update_batch_status(
                current_batch_id,
                "failed",
                str(exc),
            )
