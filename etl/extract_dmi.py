import requests
from app.database import create_source
from etl.transform import transform_observation
from etl.load import load_observation

url = "https://opendataapi.dmi.dk/v2/metObs/collections/observation/items"

params = {
    "period": "latest-10-minutes",
    "limit": 100
}

def run_dmi_etl():
    source_id = create_source("DMI")

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

    for feature in data["features"]:
        observation = transform_observation(feature, source_id)
        load_observation(observation)


    
# for feature in data["features"]:
#     observation = transform_observation(feature)
#     print(observation)





# print(data)

# print(data["features"][0])

# measurement = data["features"][0]["properties"]

# print("Parameter:", measurement["parameterId"])
# print("Værdi:", measurement["value"])
# print("Tidspunkt:", measurement["observed"])
# print("Station:", measurement["stationId"])

# for feature in data["features"]:
#     properties = feature["properties"]
#     coordinates = feature["geometry"]["coordinates"]

#     print("Station:", properties["stationId"])
#     print("Parameter:", properties["parameterId"])
#     print("Value:", properties["value"])
#     print("Observed:", properties["observed"])
#     print("Longitude:", coordinates[0])
#     print("Latitude:", coordinates[1])
#     print()