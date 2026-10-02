from app.database import create_tables
from etl.extract_dmi import run_dmi_etl

def main():
    """ Sets up the database and runs the ETL process. """

    # Create the database tables
    create_tables()

    # Run the DMI ETL process
    run_dmi_etl()

# Start the program
if __name__ == "__main__":
    main()