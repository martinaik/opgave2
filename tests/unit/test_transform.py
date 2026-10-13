# Import necessary modules
import pytest
from etl.transform import (transform_observations, validate_parameter, validate_timestamp, validate_coordinates)

def make_feature(parameter_id: str = "temp_dry", value: float = 12.5, station_id: str = "06110",
    observed: str = "2026-10-02T08:10:00Z", coordinates: list | None = None) -> dict:
    """ Create a sample observation for testing. """

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
    """ Test that measurements from the same station and time are grouped. """
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
    """ Test that a measurement outside its allowed range is rejected. """
    features = [
        make_feature("temp_dry", 12.5),
        make_feature("humidity", 150.0),
    ]

    result = transform_observations(features, 1)

    assert len(result) == 1
    assert result[0]["temp_dry"] == 12.5
    assert "humidity" not in result[0]

def test_invalid_feature_is_skipped() -> None:
    """ Test that a feature without valid properties is rejected. """
    assert transform_observations([{"geometry": {}}], 1) == []

def test_invalid_timestamp_is_skipped() -> None:
    """ Test that a feature with an invalid timestamp is rejected. """
    feature = make_feature(observed="not-a-timestamp")

    assert transform_observations([feature], 1) == []

def test_invalid_coordinates_are_skipped() -> None:
    """ Test that invalid coordinates are rejected. """
    feature = make_feature(coordinates=[200, 55.7])

    assert transform_observations([feature], 1) == []

def test_invalid_source_id_raises_error() -> None:
    """ Test that the source ID must be a positive integer. """
    with pytest.raises(ValueError):
        transform_observations([], 0)

def test_valid_temperature() -> None:
    """ Test a valid temperature. """
    assert validate_parameter("temp_dry", 12.5)

def test_invalid_temperature() -> None:
    """ Test that a temperature outside the configured range is rejected. """
    assert not validate_parameter("temp_dry", 80)

def test_valid_humidity() -> None:
    """ Test a valid humidity value. """
    assert validate_parameter("humidity", 75)

def test_invalid_humidity() -> None:
    """ Test that humidity above 100 percent is rejected. """
    assert not validate_parameter("humidity", 150)

def test_valid_wind_speed() -> None:
    """ Test that a valid wind speed is accepted. """
    assert validate_parameter("wind_speed", 10.5)

def test_negative_wind_speed_is_rejected() -> None:
    """ Test that a negative wind speed is rejected. """
    assert not validate_parameter("wind_speed", -1)

def test_valid_wind_direction() -> None:
    """ Test that a valid wind direction is accepted. """
    assert validate_parameter("wind_dir", 180)

def test_invalid_pressure_is_rejected() -> None:
    """ Test that pressure outside the configured range is rejected."""
    assert not validate_parameter("pressure_at_sea", 1200)

def test_unknown_parameter_is_accepted() -> None:
    """ Test that an unknown numeric parameter is accepted. """
    assert validate_parameter("new_parameter", 12.5)

def test_non_finite_values_are_rejected() -> None:
    """ Test that NaN and infinity are rejected. """
    assert not validate_parameter("temp_dry", float("nan"))
    assert not validate_parameter("temp_dry", float("inf"))

def test_timestamp_validation() -> None:
    """ Test valid and invalid timestamps. """
    assert validate_timestamp("2026-10-02T08:10:00Z")
    assert not validate_timestamp("not-a-timestamp")
    assert not validate_timestamp(None)

def test_coordinate_validation() -> None:
    """ Test valid and invalid coordinates. """
    assert validate_coordinates([9.5, 55.7])
    assert not validate_coordinates([200, 55.7])
    assert not validate_coordinates([9.5])

def test_non_dictionary_feature_is_skipped() -> None:
    """ Test that a non-dictionary feature is rejected. """
    assert transform_observations(["invalid feature"], 1) == []

def test_missing_station_id_is_skipped() -> None:
    """ Test that a feature without a station ID is rejected. """
    feature = make_feature()
    del feature["properties"]["stationId"]

    assert transform_observations([feature], 1) == []

def test_missing_parameter_id_is_skipped() -> None:
    """ Test that a feature without a parameter ID is rejected. """
    feature = make_feature()
    del feature["properties"]["parameterId"]

    assert transform_observations([feature], 1) == []

def test_coordinates_must_be_list_or_tuple() -> None:
    """ Test that coordinates must be a list or tuple. """
    assert not validate_coordinates("invalid")

def test_coordinates_reject_boolean_values() -> None:
    """ Test that boolean coordinates are rejected. """
    assert not validate_coordinates([True, 55.7])
    assert not validate_coordinates([9.5, False])

def test_coordinates_reject_non_finite_values() -> None:
    """ Test that infinite and NaN coordinates are rejected. """
    assert not validate_coordinates([float("inf"), 55.7])
    assert not validate_coordinates([9.5, float("nan")])

def test_coordinates_reject_out_of_range_values() -> None:
    """ Test that longitude and latitude must be in valid ranges. """
    assert not validate_coordinates([181, 55.7])
    assert not validate_coordinates([9.5, 91])

def test_parameter_rejects_none_and_boolean() -> None:
    """ Test that None and boolean measurements are rejected. """
    assert not validate_parameter("temp_dry", None)
    assert not validate_parameter("temp_dry", True)

def test_parameter_rejects_non_numeric_values() -> None:
    """ Test that non-numeric measurements are rejected. """
    assert not validate_parameter("temp_dry", "invalid")

def test_invalid_source_id_types_are_rejected() -> None:
    """ Test that invalid source ID types are rejected. """
    with pytest.raises(ValueError):
        transform_observations([], True)

    with pytest.raises(ValueError):
        transform_observations([], -1)

def test_features_must_be_a_list() -> None:
    """ Test that the input must be a list. """
    with pytest.raises(TypeError):
        transform_observations("invalid", 1)

def test_missing_geometry_is_skipped() -> None:
    """ Test that a feature without valid geometry is rejected. """
    feature = make_feature()
    del feature["geometry"]

    assert transform_observations([feature], 1) == []

def test_empty_parameter_id_is_skipped() -> None:
    """ Test that an empty parameter ID is rejected. """
    feature = make_feature(parameter_id="")

    assert transform_observations([feature], 1) == []

def test_parameter_rejects_invalid_parameter_id() -> None:
    """ Test that invalid parameter IDs are rejected. """
    assert not validate_parameter("", 12.5)
    assert not validate_parameter("   ", 12.5)
    assert not validate_parameter(None, 12.5)

