from etl.transform import transform_observation

def test_transform_observation():
    feature = {
        "properties": {
            "stationId": "06110",
            "parameterId": "temp_dry",
            "value": 12.5,
            "observed": "2026-10-02T08:10:00Z"
        },
        "geometry": {
            "coordinates": [9.5, 55.7]
        }
    }

    result = transform_observation(feature, 1)

    assert result["station_id"] == "06110"
    assert result["latitude"] == 55.7
    assert result["longitude"] == 9.5
    assert result["source_id"] == 1
    assert result["parameter_id"] == "temp_dry"
    assert result["value"] == 12.5
    assert result["observed"] == "2026-10-02T08:10:00Z"