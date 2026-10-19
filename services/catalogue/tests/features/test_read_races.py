from datetime import date

import pytest

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.race_snapshot import LapRow, PitStopRow, RaceSummary, ResultRow
from catalogue.features.read_races import (
    RaceNotIngested,
    SeasonNotLoaded,
    list_races,
    race_laps,
    race_pit_stops,
)

LOADED = RaceSummary(
    2025, 1, "Australian Grand Prix", "Albert Park", date(2025, 3, 16), ingested=True
)
SCHEDULED = RaceSummary(2025, 3, "Japanese Grand Prix", "Suzuka", date(2025, 4, 6), ingested=False)


class MemoryReader:
    def seasons(self) -> tuple[int, ...]:
        return (2025,)

    def races_of(self, season: int) -> tuple[RaceSummary, ...]:
        return (LOADED, SCHEDULED) if season == 2025 else ()

    def race(self, season: int, round_number: int) -> RaceSummary | None:
        return {1: LOADED, 3: SCHEDULED}.get(round_number) if season == 2025 else None

    def results_of(self, season: int, round_number: int) -> tuple[ResultRow, ...]:
        return ()

    def laps_of(self, season: int, round_number: int) -> tuple[LapRow, ...]:
        return (LapRow("norris", 1, 1, LapTimeMs(117099)),)

    def pit_stops_of(self, season: int, round_number: int) -> tuple[PitStopRow, ...]:
        return ()


def test_laps_of_an_ingested_race() -> None:
    assert race_laps(MemoryReader(), 2025, 1) == (LapRow("norris", 1, 1, LapTimeMs(117099)),)


def test_scheduled_but_not_ingested_race_is_not_readable() -> None:
    with pytest.raises(RaceNotIngested, match="round 3"):
        race_laps(MemoryReader(), 2025, 3)


def test_unknown_race_is_not_readable() -> None:
    with pytest.raises(RaceNotIngested, match="round 99"):
        race_pit_stops(MemoryReader(), 2025, 99)


def test_season_without_races_is_not_found() -> None:
    with pytest.raises(SeasonNotLoaded, match="1900"):
        list_races(MemoryReader(), 1900)
