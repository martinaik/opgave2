# Import necessary modules
from app.database import create_source
from etl.extract_dmi import extract_dmi
from etl.transform import transform_observations
from etl.load import load_observation

def run_dmi_etl() -> None:
    """ 
    This function extracts data from the DMI API, transforms it into the required format, 
    and loads it into the database.
    """

    # Get the source ID for DMI
    source_id = create_source("DMI")
    
    # Convert the response to json
    data = extract_dmi()

    # Transform the DMI data into the required format
    observations = transform_observations(data["features"], source_id)

    # Load each observation into the database
    for observation in observations:
        load_observation(observation)
