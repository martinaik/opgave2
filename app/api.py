from fastapi import FastAPI, HTTPException, Query
from datetime import datetime
from app.database import get_connection

app = FastAPI(
    title = "DMI Data API",
    description = "API for DMI data measurements.",
    version = "1.0.0"
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
    """ Return all measurement stations from the database. """ 
    try: 
        with get_connection() as conn: 
            with conn.cursor() as cur: 
                cur.execute(""" 
                    SELECT station_id, latitude, longitude 
                    FROM station 
                    ORDER BY station_id; 
                """) 

                rows = cur.fetchall()
                 
                return [ 
                    { 
                        "station_id": row[0], 
                        "latitude": row[1], 
                        "longitude": row[2], 
                    } 
                    for row in rows 
                ] 
            
    except Exception as exc: 
        raise HTTPException( 
            status_code=500, 
            detail="Could not retrieve stations from the database.", 
        ) from exc

@app.get("/stations/{station_id}")
def get_station(station_id: str):
    """ Returns information about a specific measurement station. """
    try:
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

                row = cur.fetchone()

                if row is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Station not found.",
                    )

                return {
                    "station_id": row[0],
                    "latitude": row[1],
                    "longitude": row[2],
                }

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
    limit: int = Query(default=100, ge=1, le=1000),
):
    """ Returns measurements filtered by station, source and time. """
    if start_time and end_time and start_time > end_time:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before or equal to end_time.",
        )

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = "SELECT * FROM measurement"
                conditions = []
                params = []

                if station_id is not None:
                    conditions.append("station_id = %s")
                    params.append(station_id)

                if source_id is not None:
                    conditions.append("source_id = %s")
                    params.append(source_id)

                if start_time is not None:
                    conditions.append("observed >= %s")
                    params.append(start_time)

                if end_time is not None:
                    conditions.append("observed <= %s")
                    params.append(end_time)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                query += " ORDER BY observed DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)

                columns = [column.name for column in cur.description]
                rows = cur.fetchall()

                return [
                    dict(zip(columns, row))
                    for row in rows
                ]

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
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT source_id, name
                    FROM source
                    ORDER BY source_id;
                """)

                rows = cur.fetchall()

                return [
                    {
                        "source_id": row[0],
                        "name": row[1],
                    }
                    for row in rows
                ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve data sources from the database.",
        ) from exc