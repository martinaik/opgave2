def transform_observation(feature, source_id):
    properties = feature["properties"]
    coordinates = feature["geometry"]["coordinates"]

    return {
        "station_id": properties["stationId"],
        "latitude": coordinates[1],
        "longitude": coordinates[0],
        "source_id": source_id,
        "parameter_id": properties["parameterId"],
        "value": properties["value"],
        "observed": properties["observed"],
    }