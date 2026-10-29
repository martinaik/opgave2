# Import necessary modules
import logging
from datetime import datetime
from math import isfinite
from numbers import Real
from typing import Any

# Set up logging
logger = logging.getLogger(__name__)

# Define parameter validation rules
PARAMETER_RULES: dict[str, tuple[float, float]] = {
    # Temperature in degrees Celsius
    "temp_dry": (-80, 60),
    "temp_dew": (-80, 60),
    "temp_mean_past1h": (-80, 60),
    "temp_max_past1h": (-80, 60),
    "temp_min_past1h": (-80, 60),
    "temp_max_past12h": (-80, 60),
    "temp_min_past12h": (-80, 60),
    "temp_grass": (-80, 60),
    "temp_grass_max_past1h": (-80, 60),
    "temp_grass_mean_past1h": (-80, 60),
    "temp_grass_min_past1h": (-80, 60),
    "temp_soil": (-80, 60),
    "temp_soil_max_past1h": (-80, 60),
    "temp_soil_mean_past1h": (-80, 60),
    "temp_soil_min_past1h": (-80, 60),

    # Relative humidity in percent
    "humidity": (0, 100),
    "humidity_past1h": (0, 100),

    # Atmospheric pressure in hPa
    "pressure": (800, 150000),
    "pressure_at_sea": (800, 1100),

    # Wind direction in degrees
    "wind_dir": (0, 360),
    "wind_dir_past1h": (0, 360),

    # Wind speed in m/s
    "wind_speed": (0, 150),
    "wind_speed_past1h": (0, 150),
    "wind_max": (0, 150),
    "wind_min": (0, 150),
    "wind_min_past1h": (0, 150),
    "wind_max_per10min_past1h": (0, 150),
    "wind_gust_always_past1h": (0, 150),
    "wind_gust_past10min": (0, 150),
    "wind_gust_last1h": (0, 150),
    "wind_gust_last3h": (0, 150),
    "wind_gust_last6h": (0, 150),

    # Precipitation in kg/m²
    "precip_past1min": (0, 500),
    "precip_past10min": (0, 500),
    "precip_past1h": (0, 1000),
    "precip_past24h": (0, 2000),

    # Precipitation duration in minutes
    "precip_dur_past10min": (0, 10),
    "precip_dur_past1h": (0, 60),

    # Snow depth
    "snow_depth_man": (0, 500),

    # Visibility in meters
    "visibility": (0, 100000),
    "visib_mean_last10min": (0, 100000),

    # Cloud height in meters
    "cloud_height": (0, 30000),

    # Radiation in W/m²
    "radia_glob": (0, 1500),
    "radia_glob_past1h": (0, 1500),

    # Duration in minutes
    "sun_last10min_glob": (0, 10),
    "sun_last1h_glob": (0, 60),
    "leav_hum_dur_past10min": (0, 10),
    "leav_hum_dur_past1h": (0, 60),
}

def validate_timestamp(observed: Any) -> bool:
    """ Checks whether a timestamp is a valid ISO 8601 string. """

    # Check if the observed value is a string and not empty
    if not isinstance(observed, str) or not observed.strip():
        return False

    # Attempt to parse the timestamp using datetime.fromisoformat
    try:
        datetime.fromisoformat(observed.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False

def validate_coordinates(coordinates: Any) -> bool:
    """ Checks whether longitude and latitude are valid coordinates. """

    # Check if coordinates is a list or tuple with at least two elements
    if not isinstance(coordinates, (list, tuple)):
        return False

    # Check if the list or tuple has at least two elements
    if len(coordinates) < 2:
        return False

    longitude, latitude = coordinates[0], coordinates[1]

    # Check if both elements are real numbers and not boolean
    if (
        not isinstance(longitude, Real)
        or isinstance(longitude, bool)
        or not isinstance(latitude, Real)
        or isinstance(latitude, bool)
    ):
        return False

    # Check if both elements are finite numbers
    if not isfinite(longitude) or not isfinite(latitude):
        return False

    # Check if the coordinates are within valid ranges
    return -180 <= longitude <= 180 and -90 <= latitude <= 90

def validate_parameter(parameter_id: str, value: Any) -> bool:
    """ Validates a numeric measurement using general quality limits. """

    # Check if the parameter ID is a non-empty string
    if not isinstance(parameter_id, str) or not parameter_id.strip():
        return False

    # Check if the value is None, a boolean, or not a finite number
    if (
        value is None
        or isinstance(value, bool)
        or not isinstance(value, Real)
        or not isfinite(value)
    ):
        return False

    # Check if the parameter ID has specific validation rules
    rule = PARAMETER_RULES.get(parameter_id)

    if rule is None:
        return True

    # Check if the value is within the specified range for the parameter
    minimum, maximum = rule
    return minimum <= value <= maximum

def transform_observations(features: list[dict[str, Any]], source_id: int) -> list[dict[str, Any]]:
    """
    Validates and transforms observations into a common data structure.

    Measurements from the same station and observation time are grouped
    into one dictionary. The input must use the normalized feature
    structure expected by this function.
    """
    # Validate the source_id and features input types
    if (
        not isinstance(source_id, int)
        or isinstance(source_id, bool)
        or source_id <= 0
    ):
        raise ValueError("source_id must be a positive integer")

    # Validate that features is a list
    if not isinstance(features, list):
        raise TypeError("features must be a list")

    # Initialize a dictionary to group observations by station and time
    observations: dict[tuple[str, str], dict[str, Any]] = {}

    # Iterate through each feature and validate its structure and values
    for feature in features:
        if not isinstance(feature, dict):
            logger.warning("Invalid feature rejected: not a dictionary")
            continue

        # Extract properties and geometry from the feature
        properties = feature.get("properties")
        geometry = feature.get("geometry")

        # Validate that properties and geometry are dictionaries
        if not isinstance(properties, dict) or not isinstance(geometry, dict):
            logger.warning(
                "Invalid feature rejected: missing properties or geometry"
            )
            continue

        # Extract relevant fields from properties and geometry
        station_id = properties.get("stationId")
        observed = properties.get("observed")
        parameter_id = properties.get("parameterId")
        value = properties.get("value")
        coordinates = geometry.get("coordinates")

        # Validate the extracted fields using the defined validation functions
        if not isinstance(station_id, str) or not station_id.strip():
            logger.warning("Invalid feature rejected: missing station ID")
            continue

        # Validate the parameter ID and value
        if not isinstance(parameter_id, str) or not parameter_id.strip():
            logger.warning(
                "Invalid feature rejected for station %s: missing parameter ID",
                station_id,
            )
            continue

        # Validate the observed timestamp
        if not validate_timestamp(observed):
            logger.warning(
                "Invalid timestamp rejected for station %s",
                station_id,
            )
            continue

        # Validate the coordinates
        if not validate_coordinates(coordinates):
            logger.warning(
                "Invalid coordinates rejected for station %s",
                station_id,
            )
            continue

        # Validate the parameter value
        if not validate_parameter(parameter_id, value):
            logger.warning(
                "Invalid measurement rejected: station=%s, parameter=%s",
                station_id,
                parameter_id,
            )
            continue

        # Use station ID and observation time as the key for grouping
        key = (station_id, observed)

        # Create a new observation if this station and time do not exist in the dictionary
        if key not in observations:
            longitude, latitude = coordinates[0], coordinates[1]

            observations[key] = {
                "station_id": station_id,
                "latitude": latitude,
                "longitude": longitude,
                "source_id": source_id,
                "observed": observed,
            }

        # Add the parameter and its value to the observation
        observations[key][parameter_id] = value

    return list(observations.values())

def transform_herodot_observations(observations: list[dict[str, Any]], source_id: int) -> list[dict[str, Any]]:
    """ Validates and transforms Herodot observations into a common data structure. 
    
    Observations from the same node and observation time are grouped into one dictionary."""

    # Validate the source ID
    if (
        not isinstance(source_id, int)
        or isinstance(source_id, bool)
        or source_id <= 0
    ):
        raise ValueError("source_id must be a positive integer")

    # Validate that observations is a list
    if not isinstance(observations, list):
        raise TypeError("observations must be a list")

    # Define the sensor names accepted from Herodot.
    sensor_columns = {
        "temperature": "temperature",
        "co2_concentration": "co2_concentration",
        "humidity": "humidity",
        "pressure": "pressure",
    }

    # Store measurements grouped by node and timestamp.
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}

    for observation in observations:
        # Validate that the observation is a dictionary
        if not isinstance(observation, dict):
            logger.warning("Invalid Herodot observation rejected")
            continue

        # Extract relevant fields from the observation
        node_id = observation.get("nodeId")
        instrument_id = observation.get("instrumentId")
        instrument_model = observation.get("instrumentModel")
        timestamp = observation.get("timestamp")
        sensor = observation.get("sensor")
        value = observation.get("value")

        # Validate the node ID
        if not isinstance(node_id, str) or not node_id.strip():
            logger.warning("Herodot observation rejected: missing node ID")
            continue

        # Validate the instrument ID
        if not isinstance(instrument_id, str) or not instrument_id.strip():
            logger.warning(
                "Herodot observation rejected: missing instrument ID"
            )
            continue

        # Validate the instrument model
        if not isinstance(instrument_model, str) or not instrument_model.strip():
            logger.warning(
                "Herodot observation rejected: missing instrument model"
            )
            continue

        # Validate the timestamp
        if not validate_timestamp(timestamp):
            logger.warning(
                "Herodot observation rejected: invalid timestamp"
            )
            continue

        # Validate the sensor name
        if sensor not in sensor_columns:
            logger.warning("Unknown Herodot sensor rejected: %s", sensor)
            continue

        # Validate the value to ensure it is a real number and not a boolean
        if not isinstance(value, Real) or isinstance(value, bool):
            logger.warning("Invalid Herodot value rejected")
            continue

        # Check if the value is finite
        if not isfinite(value):
            logger.warning("Non-finite Herodot value rejected")
            continue

        # Define valid ranges for each sensor type
        limits = {
            "temperature": (-80, 100),
            "co2_concentration": (0, 100000),
            "humidity": (0, 100),
            "pressure": (300, 150000),
        }

        minimum, maximum = limits[sensor]

        # Check if the value is within the valid range for the sensor
        if not minimum <= value <= maximum:
            logger.warning(
                "Herodot value outside valid range: sensor=%s",
                sensor,
            )
            continue

        # Round the timestamp to whole seconds so measurements
        # from the same second can be grouped together.
        parsed_timestamp = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        ).replace(microsecond=0)

        observed = parsed_timestamp.isoformat()

        # Group by node and rounded timestamp.
        key = (node_id, instrument_id, observed)

        if key not in grouped:
            grouped[key] = {
                "node_id": node_id,
                "source_id": source_id,
                "instrument_id": instrument_id,
                "instrument_model": instrument_model,
                "observed": observed,
                "temperature": None,
                "co2_concentration": None,
                "humidity": None,
                "pressure": None,
            }

        column = sensor_columns[sensor]
        grouped[key][column] = value

    return list(grouped.values())