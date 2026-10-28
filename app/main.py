# Import necessary modules
import logging
import time
from app.migrations import run_migrations
from etl.etl_dmi import run_dmi_etl
from etl.etl_herodot import run_herodot_etl

# Time between ETL runs in seconds
INTERVAL = 600  # 10 minutes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set up logging
logger = logging.getLogger(__name__)

def main() -> None:
    """ Runs migrations and both ETL processes continuously. """

    while True:
        try:
            # Run database migrations before starting the ETL processes
            logger.info("Checking database migrations...")
            run_migrations()

        # Handle any exceptions that occur during the migration process
        except Exception:
            logger.exception(
                "Could not run database migrations. "
                "Will retry in 10 minutes."
            )
            time.sleep(INTERVAL)
            continue

        # Run DMI ETL
        try:
            logger.info("Running DMI ETL...")
            run_dmi_etl()
            logger.info("DMI ETL completed.")

        except Exception:
            logger.exception("DMI ETL failed.")

        # Run Herodot ETL independently
        try:
            logger.info("Running Herodot ETL...")
            run_herodot_etl()
            logger.info("Herodot ETL completed.")

        except Exception:
            logger.exception("Herodot ETL failed.")

        # Wait before the next cycle
        logger.info("Both ETL processes have been attempted. Waiting 10 minutes...")
        time.sleep(INTERVAL)

# Run the main function
if __name__ == "__main__":
    main()
