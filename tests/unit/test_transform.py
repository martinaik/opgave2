# Import necessary modules
import pytest
from etl.transform import (transform_observations, transform_herodot_observations, validate_parameter, validate_timestamp, validate_coordinates)

def make_feature(parameter_id: str = "temp_dry", value: float = 12.5, station_id: str = "06110",
    observed: str = "2026-10-02T08:10:00Z", coordinates: list | None = None) -> dict:
    """ Creates a sample observation for testing. """

    # Set default coordinates if not provided
    if coordinates is None:
        coordinates = [9.5, 55.7]

    return {
        "properties": {
            "stationId": station_id,
            "parameterId": parameter_id,
            "value": value,
            "observed": observed,
        },
        "geometry": {
            "coordinates": coordinates,
        },
    }

def test_transform_observations() -> None:
    """ Tests that measurements from the same station and time are grouped. """

    features = [
        make_feature("temp_dry", 12.5),
        make_feature("humidity", 75.0),
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

def test_invalid_measurement_is_skipped() -> None:
    """ Tests that a measurement outside its allowed range is rejected. """

    features = [
        make_feature("temp_dry", 12.5),
        make_feature("humidity", 150.0),
    ]

    result = transform_observations(features, 1)

    assert len(result) == 1
    assert result[0]["temp_dry"] == 12.5
    assert "humidity" not in result[0]

def test_invalid_feature_is_skipped() -> None:
    """ Tests that a feature without valid properties is rejected. """

    assert transform_observations([{"geometry": {}}], 1) == []

def test_invalid_timestamp_is_skipped() -> None:
    """ Tests that a feature with an invalid timestamp is rejected. """

    feature = make_feature(observed="not-a-timestamp")

    assert transform_observations([feature], 1) == []

def test_invalid_coordinates_are_skipped() -> None:
    """ Tests that invalid coordinates are rejected. """

    feature = make_feature(coordinates=[200, 55.7])

    assert transform_observations([feature], 1) == []

def test_invalid_source_id_raises_error() -> None:
    """ Tests that the source ID must be a positive integer. """

    with pytest.raises(ValueError):
        transform_observations([], 0)

def test_valid_temperature() -> None:
    """ Tests a valid temperature. """

    assert validate_parameter("temp_dry", 12.5)

def test_invalid_temperature() -> None:
    """ Tests that a temperature outside the configured range is rejected. """

    assert not validate_parameter("temp_dry", 80)

def test_valid_humidity() -> None:
    """ Tests a valid humidity value. """

    assert validate_parameter("humidity", 75)

def test_invalid_humidity() -> None:
    """ Tests that humidity above 100 percent is rejected. """

    assert not validate_parameter("humidity", 150)

def test_valid_wind_speed() -> None:
    """ Tests that a valid wind speed is accepted. """

    assert validate_parameter("wind_speed", 10.5)

def test_negative_wind_speed_is_rejected() -> None:
    """ Tests that a negative wind speed is rejected. """

    assert not validate_parameter("wind_speed", -1)

def test_valid_wind_direction() -> None:
    """ Tests that a valid wind direction is accepted. """

    assert validate_parameter("wind_dir", 180)

def test_invalid_pressure_is_rejected() -> None:
    """ Tests that pressure outside the configured range is rejected."""

    assert not validate_parameter("pressure_at_sea", 1200)

def test_unknown_parameter_is_accepted() -> None:
    """ Tests that an unknown numeric parameter is accepted. """

    assert validate_parameter("new_parameter", 12.5)

def test_non_finite_values_are_rejected() -> None:
    """ Tests that NaN and infinity are rejected. """

    assert not validate_parameter("temp_dry", float("nan"))
    assert not validate_parameter("temp_dry", float("inf"))

def test_timestamp_validation() -> None:
    """ Tests valid and invalid timestamps. """

    assert validate_timestamp("2026-10-02T08:10:00Z")
    assert not validate_timestamp("not-a-timestamp")
    assert not validate_timestamp(None)

def test_coordinate_validation() -> None:
    """ Tests valid and invalid coordinates. """

    assert validate_coordinates([9.5, 55.7])
    assert not validate_coordinates([200, 55.7])
    assert not validate_coordinates([9.5])

def test_non_dictionary_feature_is_skipped() -> None:
    """ Tests that a non-dictionary feature is rejected. """

    assert transform_observations(["invalid feature"], 1) == []

def test_missing_station_id_is_skipped() -> None:
    """ Tests that a feature without a station ID is rejected. """

    feature = make_feature()
    del feature["properties"]["stationId"]

    assert transform_observations([feature], 1) == []

def test_missing_parameter_id_is_skipped() -> None:
    """ Tests that a feature without a parameter ID is rejected. """

    feature = make_feature()
    del feature["properties"]["parameterId"]

    assert transform_observations([feature], 1) == []

def test_coordinates_must_be_list_or_tuple() -> None:
    """ Tests that coordinates must be a list or tuple. """

    assert not validate_coordinates("invalid")

def test_coordinates_reject_boolean_values() -> None:
    """ Tests that boolean coordinates are rejected. """

    assert not validate_coordinates([True, 55.7])
    assert not validate_coordinates([9.5, False])

def test_coordinates_reject_non_finite_values() -> None:
    """ Tests that infinite and NaN coordinates are rejected. """

    assert not validate_coordinates([float("inf"), 55.7])
    assert not validate_coordinates([9.5, float("nan")])

def test_coordinates_reject_out_of_range_values() -> None:
    """ Tests that longitude and latitude must be in valid ranges. """

    assert not validate_coordinates([181, 55.7])
    assert not validate_coordinates([9.5, 91])

def test_parameter_rejects_none_and_boolean() -> None:
    """ Tests that None and boolean measurements are rejected. """

    assert not validate_parameter("temp_dry", None)
    assert not validate_parameter("temp_dry", True)

def test_parameter_rejects_non_numeric_values() -> None:
    """ Tests that non-numeric measurements are rejected. """

    assert not validate_parameter("temp_dry", "invalid")

def test_invalid_source_id_types_are_rejected() -> None:
    """ Tests that invalid source ID types are rejected. """

    with pytest.raises(ValueError):
        transform_observations([], True)

    with pytest.raises(ValueError):
        transform_observations([], -1)

def test_features_must_be_a_list() -> None:
    """ Tests that the input must be a list. """

    with pytest.raises(TypeError):
        transform_observations("invalid", 1)

def test_missing_geometry_is_skipped() -> None:
    """ Tests that a feature without valid geometry is rejected. """
    
    feature = make_feature()
    del feature["geometry"]

    assert transform_observations([feature], 1) == []

def test_empty_parameter_id_is_skipped() -> None:
    """ Tests that an empty parameter ID is rejected. """

    feature = make_feature(parameter_id="")

    assert transform_observations([feature], 1) == []

def test_parameter_rejects_invalid_parameter_id() -> None:
    """ Tests that invalid parameter IDs are rejected. """

    assert not validate_parameter("", 12.5)
    assert not validate_parameter("   ", 12.5)
    assert not validate_parameter(None, 12.5)

def make_herodot_observation(
    sensor="temperature",
    value=22.5,
    node_id="node-1",
    instrument_id="SCD41:123",
    instrument_model="SCD41",
    timestamp="2026-10-28T08:10:00.500000Z",
):
    """ Creates a sample Herodot observation for testing. """

    return {
        "nodeId": node_id,
        "instrumentId": instrument_id,
        "instrumentModel": instrument_model,
        "sensor": sensor,
        "value": value,
        "timestamp": timestamp,
    }

def test_transform_herodot_observations():
    """ Tests that valid observations are transformed into one measurement. """

    observations = [
        make_herodot_observation("temperature", 22.5),
        make_herodot_observation(
            "humidity", 55.0,
            timestamp="2026-10-28T08:10:00.900000Z",
        ),
        make_herodot_observation(
            "co2_concentration", 650,
            timestamp="2026-10-28T08:10:00.100000Z",
        ),
    ]

    result = transform_herodot_observations(observations, 2)

    assert len(result) == 1
    assert result[0]["node_id"] == "node-1"
    assert result[0]["instrument_id"] == "SCD41:123"
    assert result[0]["instrument_model"] == "SCD41"
    assert result[0]["source_id"] == 2
    assert result[0]["temperature"] == 22.5
    assert result[0]["humidity"] == 55.0
    assert result[0]["co2_concentration"] == 650
    assert result[0]["pressure"] is None
    assert result[0]["observed"] == "2026-10-28T08:10:00+00:00"

def test_transform_herodot_empty_list():
    """ Tests that an empty list returns no measurements. """

    assert transform_herodot_observations([], 1) == []

@pytest.mark.parametrize("source_id", [0, -1, True, "1"])
def test_transform_herodot_invalid_source_id(source_id):
    """ Tests that invalid source IDs raise ValueError. """

    with pytest.raises(ValueError):
        transform_herodot_observations([], source_id)

def test_transform_herodot_input_must_be_list():
    """ Tests that input other than a list raises TypeError. """

    with pytest.raises(TypeError):
        transform_herodot_observations("invalid", 1)

def test_transform_herodot_skips_non_dictionary():
    """ Tests that non-dictionary observations are ignored. """

    assert transform_herodot_observations(["invalid"], 1) == []

@pytest.mark.parametrize(
    "field",
    ["nodeId", "instrumentId", "instrumentModel", "timestamp", "sensor"],
)
def test_transform_herodot_skips_missing_required_fields(field):
    """ Tests that observations missing required fields are ignored. """

    observation = make_herodot_observation()
    observation.pop(field)

    assert transform_herodot_observations([observation], 1) == []

@pytest.mark.parametrize(
    "value",
    [None, True, "22.5", float("nan"), float("inf"), float("-inf")],
)
def test_transform_herodot_skips_invalid_values(value):
    """ Tests that non-numeric and non-finite values are rejected. """

    observation = make_herodot_observation(value=value)

    assert transform_herodot_observations([observation], 1) == []

@pytest.mark.parametrize(
    "sensor,value",
    [
        ("temperature", -81),
        ("temperature", 101),
        ("co2_concentration", -1),
        ("co2_concentration", 100001),
        ("humidity", -1),
        ("humidity", 101),
        ("pressure", 299),
        ("pressure", 150001),
    ],
)
def test_transform_herodot_rejects_values_outside_limits(sensor, value):
    """ Tests that measurements outside sensor limits are rejected. """

    observation = make_herodot_observation(sensor=sensor, value=value)

    assert transform_herodot_observations([observation], 1) == []

def test_transform_herodot_rejects_unknown_sensor():
    """ Tests that unknown sensor names are rejected."""

    observation = make_herodot_observation(sensor="unknown_sensor")

    assert transform_herodot_observations([observation], 1) == []

def test_transform_herodot_rounds_timestamp_to_seconds():
    """ Tests that microseconds are removed from the stored timestamp. """

    observation = make_herodot_observation(
        timestamp="2026-10-28T08:10:00.987654Z"
    )

    result = transform_herodot_observations([observation], 1)

    assert len(result) == 1
    assert result[0]["observed"] == "2026-10-28T08:10:00+00:00"

def test_transform_herodot_does_not_merge_different_instruments():
    """ Tests that measurements from different instruments remain separate. """
    
    observations = [
        make_herodot_observation(
            sensor="temperature",
            value=22.5,
            instrument_id="SCD41:123",
        ),
        make_herodot_observation(
            sensor="pressure",
            value=101325,
            instrument_id="BME280:456",
        ),
    ]

    result = transform_herodot_observations(observations, 1)

    assert len(result) == 2
