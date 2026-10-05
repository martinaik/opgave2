import os
import psycopg

def get_connection():
    """ Connects to the PostgreSQL database. """

    # Get the database settings from the environment variables
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

def create_tables():
    """ Creates the database tables if they do not already exist. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Create the source, station and measurement tables
            cur.execute("""
                CREATE TABLE IF NOT EXISTS source (
                    source_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE
                );

                CREATE TABLE IF NOT EXISTS station (
                    station_id VARCHAR(20) PRIMARY KEY,
                    latitude DOUBLE PRECISION,
                    longitude DOUBLE PRECISION
                );

                CREATE TABLE IF NOT EXISTS measurement (
                    measurement_id SERIAL PRIMARY KEY,
                    station_id VARCHAR(20) NOT NULL REFERENCES station(station_id),
                    source_id INTEGER NOT NULL REFERENCES source(source_id),
                    parameter_id VARCHAR(100) NOT NULL,
                    value DOUBLE PRECISION,
                    observed TIMESTAMPTZ,
                    UNIQUE (station_id, source_id, parameter_id, observed)
                );
            """)

def create_source(name):
    """ Adds a data source to the database or return its existing ID. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Add the source if it does not already exist
            cur.execute("""
                INSERT INTO source (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING
                RETURNING source_id
            """, (name,))

            result = cur.fetchone()

            # Return the new source ID
            if result:
                return result[0]

            # Find the ID if the source already exists
            cur.execute("""
                SELECT source_id
                FROM source
                WHERE name = %s
            """, (name,))

            return cur.fetchone()[0]


