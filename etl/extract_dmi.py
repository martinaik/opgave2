# Import necessary modules
import requests
from app.database import create_source
from etl.transform import transform_observations
from etl.load import load_observation

# URL for the DMI API
url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

# API parameters
params = {
    "period": "latest-10-minutes",
    "limit": 1000
}

def extract_dmi() -> dict:
    """ 
    Extracts data from the DMI API.
    Returns the JSON response as a dictionary.
    """

    # Make a GET request to the DMI API
    response = requests.get(url, params=params)

    # Check if the request was successful
    response.raise_for_status()

    return response.json()