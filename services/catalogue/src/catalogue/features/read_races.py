from typing import Protocol

from catalogue.entities.race_snapshot import LapRow, PitStopRow, RaceSummary, ResultRow


class RaceReader(Protocol):
    def seasons(self) -> tuple[int, ...]: ...

    def races_of(self, season: int) -> tuple[RaceSummary, ...]: ...

    def race(self, season: int, round_number: int) -> RaceSummary | None: ...

    def results_of(self, season: int, round_number: int) -> tuple[ResultRow, ...]: ...

    def laps_of(self, season: int, round_number: int) -> tuple[LapRow, ...]: ...

    def pit_stops_of(self, season: int, round_number: int) -> tuple[PitStopRow, ...]: ...


class SeasonNotFound(Exception):
    pass


class RaceNotIngested(Exception):
    pass


def list_seasons(reader: RaceReader) -> tuple[int, ...]:
    return reader.seasons()


def list_races(reader: RaceReader, season: int) -> tuple[RaceSummary, ...]:
    races = reader.races_of(season)
    if not races:
        raise SeasonNotFound(f"season {season} has not been loaded")
    return races


def ingested_race(reader: RaceReader, season: int, round_number: int) -> RaceSummary:
    race = reader.race(season, round_number)
    if race is None or not race.ingested:
        raise RaceNotIngested(f"season {season} round {round_number} has not been ingested")
    return race


def race_results(reader: RaceReader, season: int, round_number: int) -> tuple[ResultRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.results_of(season, round_number)


def race_laps(reader: RaceReader, season: int, round_number: int) -> tuple[LapRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.laps_of(season, round_number)


def race_pit_stops(reader: RaceReader, season: int, round_number: int) -> tuple[PitStopRow, ...]:
    ingested_race(reader, season, round_number)
    return reader.pit_stops_of(season, round_number)
