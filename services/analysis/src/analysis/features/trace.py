from dataclasses import dataclass

from analysis.entities.fastest_lap import FastestLap, fastest_by_lap
from analysis.entities.timeline import RaceTimeline
from analysis.entities.trace import DriverTrace, race_trace
from analysis.entities.units import LapNumber, Milliseconds, RoundNumber, Season
from analysis.features.race_source import RaceSource


@dataclass(frozen=True, slots=True)
class Trace:
    season: Season
    round_number: RoundNumber
    total_laps: LapNumber
    race_time_ms: Milliseconds | None
    fastest_by_lap: tuple[FastestLap, ...]
    series: tuple[DriverTrace, ...]


def build_trace(source: RaceSource, season: Season, round_number: RoundNumber) -> Trace:
    results = {row.driver_id: row for row in source.results_of(season, round_number)}
    timeline = RaceTimeline.from_laps(source.laps_of(season, round_number), driver_ids=results)
    pit_stops = source.pit_stops_of(season, round_number)
    return Trace(
        season,
        round_number,
        timeline.total_laps,
        timeline.leader_crossing(timeline.total_laps) if timeline.total_laps else None,
        fastest_by_lap(timeline),
        race_trace(timeline, results, pit_stops),
    )
