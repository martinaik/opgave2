from app.database import get_connection

def load_observation(observation):
    """ Saves an observation to the database. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:

            # Add the station to the database
            cur.execute("""
                INSERT INTO station (station_id, latitude, longitude)
                VALUES (%s, %s, %s)
                ON CONFLICT (station_id) DO NOTHING
            """, (
                observation["station_id"],
                observation["latitude"],
                observation["longitude"]
            ))

            # Add the measurement to the database
            cur.execute("""
                INSERT INTO measurement (
                    station_id,
                    source_id,
                    parameter_id,
                    value,
                    observed
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (station_id, source_id, parameter_id, observed)
                DO NOTHING
            """, (
                observation["station_id"],
                observation["source_id"],
                observation["parameter_id"],
                observation["value"],
                observation["observed"]
            ))
