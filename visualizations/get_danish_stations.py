# Import necessary libraries
import requests

def get_danish_station_ids() -> set[str]:
    """ Returns station IDs for stations located in Denmark. """

    # URL for the DMI Open Data API to retrieve station information
    url = "https://opendataapi.dmi.dk/v2/metObs/collections/station/items"

    station_ids = set()
    offset = 0
    limit = 1000

    # Loop to fetch station data in batches until all stations are retrieved 
    while True:
        # Make a GET request to the DMI API
        response = requests.get(
            url,
            params={"limit": limit, "offset": offset},
            timeout=30,
        )

        # Check if the request was successful
        response.raise_for_status()

        # Parse the JSON response and extract station information
        data = response.json()
        features = data.get("features", [])

        # Loop through the features to find stations located in Denmark
        for station in features:
            properties = station.get("properties", {})

            # Check if the station is located in Denmark and add its ID to the set
            if properties.get("country") == "DNK":
                station_id = properties.get("stationId")

                if station_id:
                    station_ids.add(str(station_id))

        # Break the loop if fewer features than the limit were returned, indicating all stations have been retrieved
        if len(features) < limit:
            break

        # Increment the offset for the next batch of stations
        offset += limit

    return station_ids

