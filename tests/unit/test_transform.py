# Import necessary modules
from etl.transform import transform_observations

def test_transform_observations() -> None:
    """ Tests transforming observations. """
    
    features = [
        {
            "properties": {
                "stationId": "06110",
                "parameterId": "temp_dry",
                "value": 12.5,
                "observed": "2026-10-02T08:10:00Z"
            },
            "geometry": {
                "coordinates": [9.5, 55.7]
            }
        },
        {
            "properties": {
                "stationId": "06110",
                "parameterId": "humidity",
                "value": 75.0,
                "observed": "2026-10-02T08:10:00Z"
            },
            "geometry": {
                "coordinates": [9.5, 55.7]
            }
        }
    ]

    result = transform_observations(features, 1)

    assert len(result) == 1

    assert result[0]["station_id"] == "06110"
    assert result[0]["latitude"] == 55.7
    assert result[0]["longitude"] == 9.5
    assert result[0]["source_id"] == 1
    assert result[0]["observed"] == "2026-10-02T08:10:00Z"

    assert result[0]["temp_dry"] == 12.5
    assert result[0]["humidity"] == 75.0