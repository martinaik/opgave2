# Import necessary modules
import logging
from app.database import create_source
from etl.extract_dmi import extract_dmi
from etl.transform import transform_observations
from etl.load import load_observation

# Set up logging
logger = logging.getLogger(__name__)

def run_dmi_etl() -> None:
    """
    Extracts data from the DMI API, transforms it,
    and loads it into the database.
    """

    # Log the start of the ETL process
    logger.info("Starting DMI ETL process.")

    # Get the source ID for DMI
    source_id = create_source("DMI")

    # Extract data from the DMI API
    data = extract_dmi()

    # Transform the DMI data into the required format
    observations = transform_observations(
        data["features"], source_id
    )

    # Load each observation into the database
    for observation in observations:
        load_observation(observation)

    # Log the completion of the ETL process
    logger.info(
        "DMI ETL process completed. "
        "%s observations processed.",
        len(observations),
    )