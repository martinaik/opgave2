def transform_observation(feature, source_id):
    """ Transforms an observation into the required format. """

    # Get the observation properties
    properties = feature["properties"]

    # Get the station coordinates
    coordinates = feature["geometry"]["coordinates"]

    # Return the observation in the required format
    return {
        "station_id": properties["stationId"],
        "latitude": coordinates[1],
        "longitude": coordinates[0],
        "source_id": source_id,
        "parameter_id": properties["parameterId"],
        "value": properties["value"],
        "observed": properties["observed"],
    }