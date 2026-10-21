from dataclasses import dataclass

from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import LapNumber, Milliseconds


@dataclass(frozen=True, slots=True)
class FastestLap:
    driver_id: str
    lap: LapNumber
    time_ms: Milliseconds


@dataclass(frozen=True, slots=True)
class Candidate:
    fastest: FastestLap
    set_at: Milliseconds


def fastest_lap(timeline: RaceTimeline, before_ms: Milliseconds | None = None) -> FastestLap | None:
    candidates: list[Candidate] = []
    for driver in timeline.drivers:
        previous = Milliseconds(0)
        for lap, crossing in enumerate(driver.crossings, start=1):
            if before_ms is None or crossing <= before_ms:
                time_ms = Milliseconds(crossing - previous)
                candidates.append(
                    Candidate(FastestLap(driver.driver_id, LapNumber(lap), time_ms), crossing)
                )
            previous = crossing
    if not candidates:
        return None
    return min(candidates, key=lambda item: (item.fastest.time_ms, item.set_at)).fastest


def fastest_by_lap(timeline: RaceTimeline) -> tuple[FastestLap, ...]:
    best: Candidate | None = None
    progression: list[FastestLap] = []
    for lap in range(1, timeline.total_laps + 1):
        candidates = [
            Candidate(
                FastestLap(driver.driver_id, LapNumber(lap), driver.lap_time(LapNumber(lap))),
                driver.crossings[lap - 1],
            )
            for driver in timeline.drivers
            if driver.laps >= lap
        ]
        lap_best = min(candidates, key=lambda item: (item.fastest.time_ms, item.set_at))
        if best is None or lap_best.fastest.time_ms < best.fastest.time_ms:
            best = lap_best
        progression.append(best.fastest)
    return tuple(progression)
