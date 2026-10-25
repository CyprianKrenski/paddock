import pytest

from catalogue.entities.errors import MalformedSourceRawData
from catalogue.entities.lap_time import parse_lap_time


def test_parses_seconds_minutes_and_hours() -> None:
    assert parse_lap_time("57.099") == 57099
    assert parse_lap_time("1:57.099") == 117099
    assert parse_lap_time("40:56.330") == 2456330
    assert parse_lap_time("1:02:03.456") == 3723456


def test_missing_time_is_none() -> None:
    assert parse_lap_time(None) is None
    assert parse_lap_time("") is None


def test_garbage_is_malformed_source_data() -> None:
    with pytest.raises(MalformedSourceRawData, match="error_value_logged"):
        parse_lap_time("error_value_logged")
