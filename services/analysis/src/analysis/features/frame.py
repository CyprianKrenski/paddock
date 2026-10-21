from dataclasses import dataclass

from analysis.entities.fastest_lap import FastestLap, fastest_lap
from analysis.entities.frame import DriverState, replay_frame
from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import Milliseconds, RoundNumber, Season
from analysis.features.race_source import RaceSource


@dataclass(frozen=True, slots=True)
class Frame:
    season: Season
    round_number: RoundNumber
    at_seconds: float
    fastest_lap: FastestLap | None
    drivers: tuple[DriverState, ...]


def build_frame(
    source: RaceSource, season: Season, round_number: RoundNumber, at_seconds: float
) -> Frame:
    results = {row.driver_id: row for row in source.results_of(season, round_number)}
    timeline = RaceTimeline.from_laps(source.laps_of(season, round_number), driver_ids=results)
    at_ms = Milliseconds(round(at_seconds * 1000))
    states = replay_frame(timeline, results, at_ms=at_ms)
    return Frame(season, round_number, at_seconds, fastest_lap(timeline, before_ms=at_ms), states)
