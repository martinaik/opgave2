# Import necessary modules
import os
import psycopg

def get_connection() -> psycopg.Connection:
    """ 
    Connects to the PostgreSQL database. 
    Returns a connection object.
    """

    # Get the database settings from the environment variables
    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )

def create_source(name: str) -> int:
    """ 
    Creates a new source in the database if it does not already exist.
    Returns the ID of the source.
    """

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

            # Get the result of the insert operation
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

            # Return the existing source ID
            return cur.fetchone()[0]


