import pytest
from src.utils.converters import kelvin_to_celsius, km_to_miles, miles_to_km


def test_kelvin_to_celsius_freezing():
    assert kelvin_to_celsius(273.15) == 0.0


def test_kelvin_to_celsius_boiling():
    assert kelvin_to_celsius(373.15) == 100.0


def test_km_to_miles_known_value():
    assert round(km_to_miles(1.0), 6) == 0.621371


def test_miles_to_km_known_value():
    assert round(miles_to_km(1.0), 3) == 1.609


def test_km_to_miles_negative_raises():
    with pytest.raises(ValueError):
        km_to_miles(-5.0)


def test_miles_to_km_negative_raises():
    with pytest.raises(ValueError):
        miles_to_km(-1.0)
