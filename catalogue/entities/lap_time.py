from catalogue.entities.units import Milliseconds


class MalformedSourceRawData(ValueError):
    pass


def parse_lap_time(text: str | None) -> Milliseconds | None:
    if not text:
        return None
    *larger_units, seconds = text.split(":")
    whole_seconds, _, fraction = seconds.partition(".")
    try:
        total_seconds = 0
        for unit in larger_units:
            total_seconds = total_seconds * 60 + int(unit)
        total_seconds = total_seconds * 60 + int(whole_seconds)
        milliseconds = int(fraction.ljust(3, "0")[:3])
    except ValueError as error:
        raise MalformedSourceRawData(f"lap time {text!r}") from error
    return Milliseconds(total_seconds * 1000 + milliseconds)
