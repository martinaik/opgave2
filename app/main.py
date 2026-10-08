# Import necessary modules
import time
from etl.etl_dmi import run_dmi_etl

# Time between DMI requests in seconds
INTERVAL = 600 # 10 minutes

def main() -> None:
    """
    Main function to run the application.
    This function sets up the database and runs the ETL process in a loop.
    """

    # Run the DMI ETL process
    while True:
        print("Running DMI ETL...")
        run_dmi_etl()
        print("DMI ETL completed. Waiting 10 minutes...")

        time.sleep(INTERVAL)

# Start the program
if __name__ == "__main__":
    main()
