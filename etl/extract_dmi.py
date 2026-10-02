import requests
from app.database import create_source
from etl.transform import transform_observation
from etl.load import load_observation

# URL for the DMI API
url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

# API parameters
params = {
    "period": "latest-10-minutes",
    "limit": 100
}

def run_dmi_etl():
    """ Retrieves observations from DMI's API and loads them into the database. """

    # Get the source ID for DMI
    source_id = create_source("DMI")

    # Get data from the DMI API
    response = requests.get(url, params=params)

    # Check if the request was successful
    response.raise_for_status()

    # Convert the response to json
    data = response.json()

    for feature in data["features"]:
        # Transform the observation
        observation = transform_observation(feature, source_id)

        # Save the observation to the database
        load_observation(observation)
