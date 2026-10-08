def transform_observations(features: list, source_id: int) -> list:
    """ Transforms observations into the required format.
     Args:
        features: A list of features from the DMI API.
        source_id: The ID of the data source.

     Returns:
        A list of transformed observations.
    """

    observations = {} # Use a dictionary to group observations by station and time

    for feature in features:
        # Get the observation properties
        properties = feature["properties"]

        # Get the station coordinates
        coordinates = feature["geometry"]["coordinates"]

        # Get observation values
        station_id = properties["stationId"]
        observed = properties["observed"]
        parameter_id = properties["parameterId"]
        value = properties["value"]

        # Use station ID and observation time as the key
        key = (station_id, observed)

        # Create a new observation if this station and time do not exist
        if key not in observations:
            observations[key] = {
                "station_id": station_id,
                "latitude": coordinates[1],
                "longitude": coordinates[0],
                "source_id": source_id,
                "observed": observed
            }

        # Add the parameter and its value to the observation
        observations[key][parameter_id] = value

    return list(observations.values())