from dataclasses import dataclass

from analysis.entities.fastest_lap import FastestLap, fastest_lap
from analysis.entities.timeline import RaceTimeline
from analysis.entities.trace import DriverTrace, race_trace
from analysis.entities.units import LapNumber, RoundNumber, Season
from analysis.features.race_source import RaceSource


@dataclass(frozen=True, slots=True)
class Trace:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    fastest_lap: FastestLap | None
    series: tuple[DriverTrace, ...]


def build_trace(source: RaceSource, season: Season, round_number: RoundNumber) -> Trace:
    timeline = RaceTimeline.from_laps(source.laps_of(season, round_number))
    total_laps = max((driver.laps for driver in timeline.drivers), default=LapNumber(0))
    return Trace(season, round_number, total_laps, fastest_lap(timeline), race_trace(timeline))
