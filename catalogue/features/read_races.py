from typing import Protocol

from catalogue.entities.race_snapshot import (
    LapRow,
    PitStopRow,
    RaceSummary,
    ResultRow,
    StandingRow,
)
from catalogue.entities.units import RoundNumber, Season


class RaceReader(Protocol):
    def seasons(self) -> tuple[Season, ...]: ...

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]: ...

    def race(self, season: Season, round_number: RoundNumber) -> RaceSummary | None: ...

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]: ...

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]: ...

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]: ...

    def standings_after(
        self, season: Season, round_number: RoundNumber
    ) -> tuple[StandingRow, ...]: ...


class SeasonNotLoaded(Exception):
    pass


class RaceNotIngested(Exception):
    pass


class StandingsNotLoaded(Exception):
    pass


def list_races(reader: RaceReader, season: Season) -> tuple[RaceSummary, ...]:
    races = reader.races_of(season)
    if not races:
        raise SeasonNotLoaded(f"season {season} has not been loaded")
    return races


def ingested_race(reader: RaceReader, season: Season, round_number: RoundNumber) -> RaceSummary:
    race = reader.race(season, round_number)
    if race is None or not race.ingested:
        raise RaceNotIngested(f"season {season} round {round_number} has not been ingested")
    return race


def race_results(
    reader: RaceReader, season: Season, round_number: RoundNumber
) -> tuple[ResultRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.results_of(season, round_number)


def race_laps(reader: RaceReader, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.laps_of(season, round_number)


def race_pit_stops(
    reader: RaceReader, season: Season, round_number: RoundNumber
) -> tuple[PitStopRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.pit_stops_of(season, round_number)


def season_standings(
    reader: RaceReader, season: Season, round_number: RoundNumber
) -> tuple[StandingRow, ...]:
    if round_number == 0:
        return ()
    rows = reader.standings_after(season, round_number)
    if not rows:
        raise StandingsNotLoaded(f"standings after season {season} round {round_number} not loaded")
    return rows
