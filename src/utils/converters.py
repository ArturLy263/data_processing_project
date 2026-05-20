KM_TO_MI_FACTOR = 0.621371


def kelvin_to_celsius(value: float) -> float:
    return value - 273.15


def kelvin_to_celsius_many(values):
    for value in values:
        yield value - 273.15


def km_to_miles(value: float) -> float:
    if value < 0:
        raise ValueError(f"Расстояние не может быть отрицательным: {value}")
    return value * KM_TO_MI_FACTOR


def miles_to_km(value: float) -> float:
    if value < 0:
        raise ValueError(f"Расстояние не может быть отрицательным: {value}")
    return value / KM_TO_MI_FACTOR