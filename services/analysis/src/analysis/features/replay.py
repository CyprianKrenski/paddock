from collections.abc import Mapping
from dataclasses import dataclass

from analysis.entities.fastest_lap import FastestLapEvent, fastest_lap_events
from analysis.entities.replay import DriverReplay, driver_keyframes
from analysis.entities.rows import ResultRow
from analysis.entities.timeline import DriverTimeline, RaceTimeline
from analysis.entities.units import LapNumber, Milliseconds, RoundNumber, Season
from analysis.features.race_source import RaceSource


@dataclass(frozen=True, slots=True)
class Replay:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    fastest_laps: tuple[FastestLapEvent, ...]
    drivers: tuple[DriverReplay, ...]


def build_replay(source: RaceSource, season: Season, round_number: RoundNumber) -> Replay:
    results = {row.driver_id: row for row in source.results_of(season, round_number)}
    timeline = RaceTimeline.from_laps(source.laps_of(season, round_number), driver_ids=results)
    pits: dict[str, dict[LapNumber, Milliseconds | None]] = {}
    for stop in source.pit_stops_of(season, round_number):
        laps = pits.setdefault(stop.driver_id, {})
        known = laps.get(stop.lap)
        if stop.duration_ms is None or (stop.lap in laps and known is None):
            laps[stop.lap] = None
        else:
            laps[stop.lap] = Milliseconds((known or 0) + stop.duration_ms)
    return Replay(
        season,
        round_number,
        timeline.total_laps,
        fastest_lap_events(timeline),
        tuple(
            driver_replay(driver, results.get(driver.driver_id), pits.get(driver.driver_id, {}))
            for driver in timeline.drivers
        ),
    )


def driver_replay(
    driver: DriverTimeline,
    result: ResultRow | None,
    pit_stops: Mapping[LapNumber, Milliseconds | None],
) -> DriverReplay:
    return DriverReplay(
        driver.driver_id,
        result.code if result else None,
        result.constructor_id if result else None,
        result.grid if result else None,
        result is not None and result.classified,
        driver_keyframes(driver, pit_stops),
    )
