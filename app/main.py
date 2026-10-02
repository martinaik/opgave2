from app.database import create_tables
from etl.extract_dmi import run_dmi_etl

def main():
    create_tables()

    run_dmi_etl()

if __name__ == "__main__":
    main()