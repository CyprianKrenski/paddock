from dataclasses import dataclass
from typing import Protocol

from catalogue.entities.errors import MalformedSourceRawData
from catalogue.entities.lap_time import parse_lap_time
from catalogue.entities.race_snapshot import (
    DriverInfo,
    LapRow,
    PitStopRow,
    RaceInfo,
    RaceSnapshot,
    ResultRow,
)
from catalogue.entities.units import LapNumber, Position, RoundNumber, Season
from catalogue.infrastructure.jolpica_pages import (
    FetchJson,
    ResultsRace,
    fetch_lap_timings,
    fetch_pit_stops,
    fetch_race_results,
)


class RaceStore(Protocol):
    def save(self, snapshot: RaceSnapshot) -> None: ...


class RaceNotFound(Exception):
    pass


@dataclass(frozen=True, slots=True)
class IngestSummary:
    drivers: int
    laps: int
    pit_stops: int


def ingest_race(
    fetch: FetchJson, store: RaceStore, season: Season, round_number: RoundNumber
) -> IngestSummary:
    results = fetch_race_results(fetch, season, round_number)
    if results is None:
        raise RaceNotFound(f"season {season} round {round_number} is unknown to the source")
    snapshot = build_snapshot(results, fetch, season, round_number)
    store.save(snapshot)
    return IngestSummary(
        drivers=len(snapshot.drivers), laps=len(snapshot.laps), pit_stops=len(snapshot.pit_stops)
    )


def build_snapshot(
    results: ResultsRace, fetch: FetchJson, season: Season, round_number: RoundNumber
) -> RaceSnapshot:
    drivers = tuple(
        DriverInfo(
            id=entry.driver.driver_id,
            code=entry.driver.code,
            given_name=entry.driver.given_name,
            family_name=entry.driver.family_name,
        )
        for entry in results.results
    )
    known = {driver.id for driver in drivers}
    laps = tuple(
        LapRow(
            driver_id=known_driver(timing.driver_id, known),
            lap=LapNumber(timing.lap),
            position=Position(timing.position),
            time_ms=parse_lap_time(timing.time),
        )
        for timing in fetch_lap_timings(fetch, season, round_number)
    )
    pit_stops = tuple(
        PitStopRow(
            driver_id=known_driver(entry.driver_id, known),
            stop=entry.stop,
            lap=LapNumber(entry.lap),
            duration_ms=parse_lap_time(entry.duration),
        )
        for entry in fetch_pit_stops(fetch, season, round_number)
    )
    return RaceSnapshot(
        race=RaceInfo(
            season=Season(results.season),
            round_number=RoundNumber(results.round_number),
            name=results.name,
            circuit_id=results.circuit.circuit_id,
            circuit_name=results.circuit.circuit_name,
            date=results.date,
            total_laps=max((LapNumber(entry.laps) for entry in results.results), default=None),
        ),
        drivers=drivers,
        results=tuple(
            ResultRow(
                driver_id=entry.driver.driver_id,
                position=Position(entry.position) if entry.position is not None else None,
                grid=Position(entry.grid),
                laps=LapNumber(entry.laps),
                status=entry.status,
            )
            for entry in results.results
        ),
        laps=laps,
        pit_stops=pit_stops,
    )


def known_driver(driver_id: str, known: set[str]) -> str:
    if driver_id not in known:
        raise MalformedSourceRawData(f"driver {driver_id!r} has laps or stops but no result row")
    return driver_id
