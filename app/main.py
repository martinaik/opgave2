# Import necessary modules
import logging
import time
from app.migrations import run_migrations
from etl.etl_dmi import run_dmi_etl

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
    """ Runs database migrations and the ETL process continuously. """
    while True:
        try:
            # Run migrations before starting the ETL process
            logger.info("Checking database migrations...")
            run_migrations()

            # Run the ETL process
            logger.info("Running DMI ETL...")
            run_dmi_etl()

            # Log that the ETL process completed successfully
            logger.info("DMI ETL completed. Waiting 10 minutes...")

        # Handle any exceptions that occur during the ETL process
        except Exception:
            logger.exception(
                "ETL cycle failed. "
                "The program will try again in 10 minutes."
            )

        # Wait for the specified interval before the next cycle
        time.sleep(INTERVAL)

# Run the main function
if __name__ == "__main__":
    main()