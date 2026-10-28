# Import necessary modules
import logging
import time
import psycopg
from app.database import get_connection

# Set up logging
logger = logging.getLogger(__name__)

# Constants for retrying database operations
MAX_RETRIES = 6
RETRY_DELAY = 5

def load_observation_once(observation: dict) -> None:
    """ 
    Loads an observation into the database. 
    If the observation already exists, it updates the existing record.
    """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert the station into the station table
            cur.execute("""
                INSERT INTO station (station_id, latitude, longitude)
                VALUES (%s, %s, %s)
                ON CONFLICT (station_id) DO NOTHING
            """, (
                observation["station_id"],
                observation["latitude"],
                observation["longitude"]
            ))

            # Insert the observation into the measurement table
            cur.execute("""
                INSERT INTO dmi_measurement (station_id, source_id, observed,
                    temp_dry,
                    temp_dew,
                    temp_mean_past1h,
                    temp_max_past1h,
                    temp_min_past1h,
                    temp_max_past12h,
                    temp_min_past12h,
                    temp_grass,
                    temp_grass_max_past1h,
                    temp_grass_mean_past1h,
                    temp_grass_min_past1h,
                    temp_soil,
                    temp_soil_max_past1h,
                    temp_soil_mean_past1h,
                    temp_soil_min_past1h,
                    humidity,
                    humidity_past1h,
                    pressure,
                    pressure_at_sea,
                    wind_dir,
                    wind_dir_past1h,
                    wind_speed,
                    wind_speed_past1h,
                    wind_gust_always_past1h,
                    wind_gust_past10min,
                    wind_gust_last1h,
                    wind_gust_last3h,
                    wind_gust_last6h,
                    wind_max,
                    wind_min_past1h,
                    wind_min,
                    wind_max_per10min_past1h,
                    precip_past1h,
                    precip_past10min,
                    precip_past1min,
                    precip_past24h,
                    precip_dur_past10min,
                    precip_dur_past1h,
                    snow_depth_man,
                    snow_cover_man,
                    visibility,
                    visib_mean_last10min,
                    cloud_cover,
                    cloud_height,
                    weather,
                    radia_glob,
                    radia_glob_past1h,
                    sun_last10min_glob,
                    sun_last1h_glob,
                    leav_hum_dur_past10min,
                    leav_hum_dur_past1h
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (station_id, source_id, observed)
                DO UPDATE SET
                    temp_dry = COALESCE(EXCLUDED.temp_dry, dmi_measurement.temp_dry),
                    temp_dew = COALESCE(EXCLUDED.temp_dew, dmi_measurement.temp_dew),
                    temp_mean_past1h = COALESCE(EXCLUDED.temp_mean_past1h, dmi_measurement.temp_mean_past1h),
                    temp_max_past1h = COALESCE(EXCLUDED.temp_max_past1h, dmi_measurement.temp_max_past1h),
                    temp_min_past1h = COALESCE(EXCLUDED.temp_min_past1h, dmi_measurement.temp_min_past1h),
                    temp_max_past12h = COALESCE(EXCLUDED.temp_max_past12h, dmi_measurement.temp_max_past12h),
                    temp_min_past12h = COALESCE(EXCLUDED.temp_min_past12h, dmi_measurement.temp_min_past12h),
                    temp_grass = COALESCE(EXCLUDED.temp_grass, dmi_measurement.temp_grass),
                    temp_grass_max_past1h = COALESCE(EXCLUDED.temp_grass_max_past1h, dmi_measurement.temp_grass_max_past1h),
                    temp_grass_mean_past1h = COALESCE(EXCLUDED.temp_grass_mean_past1h, dmi_measurement.temp_grass_mean_past1h),
                    temp_grass_min_past1h = COALESCE(EXCLUDED.temp_grass_min_past1h, dmi_measurement.temp_grass_min_past1h),
                    temp_soil = COALESCE(EXCLUDED.temp_soil, dmi_measurement.temp_soil),
                    temp_soil_max_past1h = COALESCE(EXCLUDED.temp_soil_max_past1h, dmi_measurement.temp_soil_max_past1h),
                    temp_soil_mean_past1h = COALESCE(EXCLUDED.temp_soil_mean_past1h, dmi_measurement.temp_soil_mean_past1h),
                    temp_soil_min_past1h = COALESCE(EXCLUDED.temp_soil_min_past1h, dmi_measurement.temp_soil_min_past1h),
                    humidity = COALESCE(EXCLUDED.humidity, dmi_measurement.humidity),
                    humidity_past1h = COALESCE(EXCLUDED.humidity_past1h, dmi_measurement.humidity_past1h),
                    pressure = COALESCE(EXCLUDED.pressure, dmi_measurement.pressure),
                    pressure_at_sea = COALESCE(EXCLUDED.pressure_at_sea, dmi_measurement.pressure_at_sea),
                    wind_dir = COALESCE(EXCLUDED.wind_dir, dmi_measurement.wind_dir),
                    wind_dir_past1h = COALESCE(EXCLUDED.wind_dir_past1h, dmi_measurement.wind_dir_past1h),
                    wind_speed = COALESCE(EXCLUDED.wind_speed, dmi_measurement.wind_speed),
                    wind_speed_past1h = COALESCE(EXCLUDED.wind_speed_past1h, dmi_measurement.wind_speed_past1h),
                    wind_gust_always_past1h = COALESCE(EXCLUDED.wind_gust_always_past1h, dmi_measurement.wind_gust_always_past1h),
                    wind_gust_past10min = COALESCE(EXCLUDED.wind_gust_past10min, dmi_measurement.wind_gust_past10min),
                    wind_gust_last1h = COALESCE(EXCLUDED.wind_gust_last1h, dmi_measurement.wind_gust_last1h),
                    wind_gust_last3h = COALESCE(EXCLUDED.wind_gust_last3h, dmi_measurement.wind_gust_last3h),
                    wind_gust_last6h = COALESCE(EXCLUDED.wind_gust_last6h, dmi_measurement.wind_gust_last6h),
                    wind_max = COALESCE(EXCLUDED.wind_max, dmi_measurement.wind_max),
                    wind_min_past1h = COALESCE(EXCLUDED.wind_min_past1h, dmi_measurement.wind_min_past1h),
                    wind_min = COALESCE(EXCLUDED.wind_min, dmi_measurement.wind_min),
                    wind_max_per10min_past1h = COALESCE(EXCLUDED.wind_max_per10min_past1h, dmi_measurement.wind_max_per10min_past1h),
                    precip_past1h = COALESCE(EXCLUDED.precip_past1h, dmi_measurement.precip_past1h),
                    precip_past10min = COALESCE(EXCLUDED.precip_past10min, dmi_measurement.precip_past10min),
                    precip_past1min = COALESCE(EXCLUDED.precip_past1min, dmi_measurement.precip_past1min),
                    precip_past24h = COALESCE(EXCLUDED.precip_past24h, dmi_measurement.precip_past24h),
                    precip_dur_past10min = COALESCE(EXCLUDED.precip_dur_past10min, dmi_measurement.precip_dur_past10min),
                    precip_dur_past1h = COALESCE(EXCLUDED.precip_dur_past1h, dmi_measurement.precip_dur_past1h),
                    snow_depth_man = COALESCE(EXCLUDED.snow_depth_man, dmi_measurement.snow_depth_man),
                    snow_cover_man = COALESCE(EXCLUDED.snow_cover_man, dmi_measurement.snow_cover_man),
                    visibility = COALESCE(EXCLUDED.visibility, dmi_measurement.visibility),
                    visib_mean_last10min = COALESCE(EXCLUDED.visib_mean_last10min, dmi_measurement.visib_mean_last10min),
                    cloud_cover = COALESCE(EXCLUDED.cloud_cover, dmi_measurement.cloud_cover),
                    cloud_height = COALESCE(EXCLUDED.cloud_height, dmi_measurement.cloud_height),
                    weather = COALESCE(EXCLUDED.weather, dmi_measurement.weather),
                    radia_glob = COALESCE(EXCLUDED.radia_glob, dmi_measurement.radia_glob),
                    radia_glob_past1h = COALESCE(EXCLUDED.radia_glob_past1h, dmi_measurement.radia_glob_past1h),
                    sun_last10min_glob = COALESCE(EXCLUDED.sun_last10min_glob, dmi_measurement.sun_last10min_glob),
                    sun_last1h_glob = COALESCE(EXCLUDED.sun_last1h_glob, dmi_measurement.sun_last1h_glob),
                    leav_hum_dur_past10min = COALESCE(EXCLUDED.leav_hum_dur_past10min, dmi_measurement.leav_hum_dur_past10min),
                    leav_hum_dur_past1h = COALESCE(EXCLUDED.leav_hum_dur_past1h, dmi_measurement.leav_hum_dur_past1h)
            """, (
                observation["station_id"],
                observation["source_id"],
                observation["observed"],

                observation.get("temp_dry"),
                observation.get("temp_dew"),
                observation.get("temp_mean_past1h"),
                observation.get("temp_max_past1h"),
                observation.get("temp_min_past1h"),
                observation.get("temp_max_past12h"),
                observation.get("temp_min_past12h"),
                observation.get("temp_grass"),
                observation.get("temp_grass_max_past1h"),
                observation.get("temp_grass_mean_past1h"),
                observation.get("temp_grass_min_past1h"),
                observation.get("temp_soil"),
                observation.get("temp_soil_max_past1h"),
                observation.get("temp_soil_mean_past1h"),
                observation.get("temp_soil_min_past1h"),
                observation.get("humidity"),
                observation.get("humidity_past1h"),
                observation.get("pressure"),
                observation.get("pressure_at_sea"),
                observation.get("wind_dir"),
                observation.get("wind_dir_past1h"),
                observation.get("wind_speed"),
                observation.get("wind_speed_past1h"),
                observation.get("wind_gust_always_past1h"),
                observation.get("wind_gust_past10min"),
                observation.get("wind_gust_last1h"),
                observation.get("wind_gust_last3h"),
                observation.get("wind_gust_last6h"),
                observation.get("wind_max"),
                observation.get("wind_min_past1h"),
                observation.get("wind_min"),
                observation.get("wind_max_per10min_past1h"),
                observation.get("precip_past1h"),
                observation.get("precip_past10min"),
                observation.get("precip_past1min"),
                observation.get("precip_past24h"),
                observation.get("precip_dur_past10min"),
                observation.get("precip_dur_past1h"),
                observation.get("snow_depth_man"),
                observation.get("snow_cover_man"),
                observation.get("visibility"),
                observation.get("visib_mean_last10min"),
                observation.get("cloud_cover"),
                observation.get("cloud_height"),
                observation.get("weather"),
                observation.get("radia_glob"),
                observation.get("radia_glob_past1h"),
                observation.get("sun_last10min_glob"),
                observation.get("sun_last1h_glob"),
                observation.get("leav_hum_dur_past10min"),
                observation.get("leav_hum_dur_past1h")
            ))

def load_observation(observation: dict) -> None:
    """ Loads an observation, retrying temporary database errors. """

    # Retry loading the observation in case of temporary database errors
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            load_observation_once(observation)
            return

        # Handle temporary database connection errors
        except (
            psycopg.OperationalError,
            psycopg.InterfaceError,
        ) as error:
            # Log the temporary database error and retry
            logger.warning(
                "Database connection failed "
                "(attempt %s/%s): %s",
                attempt,
                MAX_RETRIES,
                error,
            )

            # Attempt to retry the operation if we haven't reached the maximum number of retries
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * attempt

                # Log the retry attempt and wait before trying again
                logger.info(
                    "Retrying database operation in %s seconds.",
                    delay,
                )

                time.sleep(delay)

            else:
                # Log the failure after all attempts and raise the exception
                logger.exception(
                    "Could not save observation after %s attempts.",
                    MAX_RETRIES,
                )
                raise

def load_herodot_observation_once(observation: dict) -> None:
    """ Loads a transformed Herodot observation into PostgreSQL. """

    # Connect to the database
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Insert the Herodot observation into the herodot_measurement table
            cur.execute(
                """
                INSERT INTO herodot_measurement (
                    node_id,
                    instrument_id,
                    instrument_model,
                    source_id,
                    observed,
                    temperature,
                    co2_concentration,
                    humidity,
                    pressure
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (node_id, instrument_id, source_id, observed)
                DO UPDATE SET
                    temperature = COALESCE(
                        EXCLUDED.temperature,
                        herodot_measurement.temperature
                    ),
                    co2_concentration = COALESCE(
                        EXCLUDED.co2_concentration,
                        herodot_measurement.co2_concentration
                    ),
                    humidity = COALESCE(
                        EXCLUDED.humidity,
                        herodot_measurement.humidity
                    ),
                    pressure = COALESCE(
                        EXCLUDED.pressure,
                        herodot_measurement.pressure
                    );
                """,
                (
                    observation["node_id"],
                    observation.get("instrument_id"),
                    observation.get("instrument_model"),
                    observation["source_id"],
                    observation["observed"],
                    observation.get("temperature"),
                    observation.get("co2_concentration"),
                    observation.get("humidity"),
                    observation.get("pressure"),
                ),
            )

def load_herodot_observation(observation: dict) -> None:
    """ Loads a Herodot observation with retries for temporary database errors. """

    # Retry loading the Herodot observation in case of temporary database errors
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            load_herodot_observation_once(observation)
            return

        # Handle temporary database connection errors
        except (
            psycopg.OperationalError,
            psycopg.InterfaceError,
        ):
            logger.warning(
                "Database connection failed while loading Herodot "
                "(attempt %s/%s)",
                attempt,
                MAX_RETRIES,
                exc_info=True,
            )

            # Attempt to retry the operation if we haven't reached the maximum number of retries
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * attempt
                logger.info("Retrying in %s seconds.", delay)
                time.sleep(delay)
            else:
                logger.exception(
                    "Could not save Herodot observation after %s attempts.",
                    MAX_RETRIES,
                )
                raise
