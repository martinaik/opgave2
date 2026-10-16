# Import necessary modules
from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from app.database import get_connection

# Set up FastAPI application
app = FastAPI(
    title = "DMI Data API",
    description = "API for DMI data measurements."
)

@app.get("/")
def root():
    """ Returns a welcome message for the DMI Data API. """
    return {"message": "Welcome to the DMI Data API!"}

@app.get("/health")
def health_check():
    """ Checks whether the API is healthy and running. """
    return {"status": "ok"}

@app.get("/stations") 
def get_stations(): 
    """ Returns all measurement stations from the database. """ 
    try: 
        # Get a connection to the database and fetch all stations
        with get_connection() as conn: 
            with conn.cursor() as cur: 
                cur.execute(""" 
                    SELECT station_id, latitude, longitude 
                    FROM station 
                    ORDER BY station_id; 
                """) 

                # Fetch the rows from the query result
                rows = cur.fetchall()

                # Return a list of stations with their IDs and coordinates
                return [ 
                    { 
                        "station_id": row[0], 
                        "latitude": row[1], 
                        "longitude": row[2], 
                    } 
                    for row in rows 
                ] 

    # Handle any exceptions that occur during the database query
    except Exception as exc: 
        raise HTTPException( 
            status_code=500, 
            detail="Could not retrieve stations from the database.", 
        ) from exc

@app.get("/stations/{station_id}")
def get_station(station_id: str):
    """ Returns information about a specific measurement station. """
    try:
        # Get a connection to the database and fetch the station by the given ID
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT station_id, latitude, longitude
                    FROM station
                    WHERE station_id = %s;
                    """,
                    (station_id,),
                )

                # Fetch the row from the query result
                row = cur.fetchone()

                # If the station is not found, raise a 404 error
                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Station not found.",
                    )

                # Return the station information as a dictionary
                return {
                    "station_id": row[0],
                    "latitude": row[1],
                    "longitude": row[2],
                }

    # Handle any exceptions that occur during the database query
    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve station from the database.",
        ) from exc

@app.get("/measurements")
def get_measurements(
    station_id: str | None = None,
    source_id: int | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    limit: int = Query(default=1000, ge=1, le=1000),
):
    """ Returns measurements filtered by station, source and time. """

    # Validate that start_time is before or equal to end_time
    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before or equal to end_time.",
        )

    try:
        # Get a connection to the database and fetch measurements based on the provided filters
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM measurement"
                conditions = []
                params = []

                # Add conditions for filtering based on the station_id
                if station_id is not None:
                    conditions.append("station_id = %s")
                    params.append(station_id)

                # Add conditions for filtering based on the source_id
                if source_id is not None:
                    conditions.append("source_id = %s")
                    params.append(source_id)

                # Add conditions for filtering based on the start_time
                if start_time is not None:
                    conditions.append("observed >= %s")
                    params.append(start_time)

                # Add conditions for filtering based on the end_time
                if end_time is not None:
                    conditions.append("observed <= %s")
                    params.append(end_time)

                # If there are any conditions, append them to the query
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                # Add ordering and limit to the query
                query += " ORDER BY observed DESC LIMIT %s"
                params.append(limit)

                # Execute the query with the provided parameters
                cur.execute(query, params)

                # Fetch the column names and rows from the query result
                columns = [column.name for column in cur.description]
                rows = cur.fetchall()

                # Return the measurements as a list of dictionaries
                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

    # Handle any exceptions that occur during the database query
    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve measurements from the database.",
        ) from exc

@app.get("/sources")
def get_sources():
    """ Returns all data sources from the database. """

    try:
        # Get a connection to the database and fetch all sources
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT source_id, name
                    FROM source
                    ORDER BY source_id;
                """)

                # Fetch the rows from the query result
                rows = cur.fetchall()

                # Return the sources as a list of dictionaries
                return [
                    {
                        "source_id": row[0],
                        "name": row[1],
                    }
                    for row in rows
                ]
    # Handle any exceptions that occur during the database query
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve data sources from the database.",
        ) from exc
