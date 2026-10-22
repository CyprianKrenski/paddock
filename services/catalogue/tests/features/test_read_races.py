from datetime import date

import pytest

from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.race_snapshot import (
    LapRow,
    PitStopRow,
    RaceSummary,
    ResultRow,
    StandingRow,
)
from catalogue.entities.units import LapNumber, Position, RoundNumber, Season
from catalogue.features.read_races import (
    RaceNotIngested,
    SeasonNotLoaded,
    StandingsNotLoaded,
    list_races,
    race_laps,
    race_pit_stops,
    season_standings,
)

LOADED = RaceSummary(
    Season(2025),
    RoundNumber(1),
    "Australian Grand Prix",
    "Albert Park",
    date(2025, 3, 16),
    ingested=True,
)
SCHEDULED = RaceSummary(
    Season(2025), RoundNumber(3), "Japanese Grand Prix", "Suzuka", date(2025, 4, 6), ingested=False
)


class MemoryReader:
    def seasons(self) -> tuple[Season, ...]:
        return (Season(2025),)

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        return (LOADED, SCHEDULED) if season == 2025 else ()

    def race(self, season: Season, round_number: RoundNumber) -> RaceSummary | None:
        return {1: LOADED, 3: SCHEDULED}.get(round_number) if season == 2025 else None

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        return ()

    def standings_after(self, season: Season, round_number: RoundNumber) -> tuple[StandingRow, ...]:
        return (StandingRow("norris", Position(1), 44.0, 1),) if round_number == 1 else ()

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        return (LapRow("norris", LapNumber(1), Position(1), LapTimeMs(117099)),)

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]:
        return ()


def test_laps_of_an_ingested_race() -> None:
    assert race_laps(MemoryReader(), Season(2025), RoundNumber(1)) == (
        LapRow("norris", LapNumber(1), Position(1), LapTimeMs(117099)),
    )


def test_scheduled_but_not_ingested_race_is_not_readable() -> None:
    with pytest.raises(RaceNotIngested, match="round 3"):
        race_laps(MemoryReader(), Season(2025), RoundNumber(3))


def test_unknown_race_is_not_readable() -> None:
    with pytest.raises(RaceNotIngested, match="round 99"):
        race_pit_stops(MemoryReader(), Season(2025), RoundNumber(99))


def test_season_without_races_is_not_found() -> None:
    with pytest.raises(SeasonNotLoaded, match="1900"):
        list_races(MemoryReader(), Season(1900))


def test_standings_before_the_season_are_empty_and_missing_rounds_are_an_error() -> None:
    assert season_standings(MemoryReader(), Season(2025), RoundNumber(0)) == ()
    assert season_standings(MemoryReader(), Season(2025), RoundNumber(1)) == (
        StandingRow("norris", Position(1), 44.0, 1),
    )
    with pytest.raises(StandingsNotLoaded, match="round 2"):
        season_standings(MemoryReader(), Season(2025), RoundNumber(2))
