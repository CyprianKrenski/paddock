from dataclasses import dataclass
from math import ceil
from typing import Any

from web.entities.standings import laps_down_text, race_time_text
from web.entities.teams import line_styles, team_name
from web.entities.units import Milliseconds
from web.entities.views import DriverReplay, Replay

JsonObject = dict[str, Any]

VIEWPORT = 960
PX_PER_SECOND = 4
ROW_HEIGHT = 24
TOP = 28
BOTTOM = 36
AFTER_FINISH_MS = 5000


@dataclass(frozen=True, slots=True)
class ReplayLayout:
    viewport: int
    px_per_second: int
    row_height: int
    top: int
    rows: int
    height: int
    duration_ms: Milliseconds


def replay_layout(replay: Replay) -> ReplayLayout:
    frames = [frame for driver in replay.drivers for frame in driver.keyframes]
    last_ms = max((frame.at_ms for frame in frames), default=0)
    duration = Milliseconds(ceil(last_ms / 1000) * 1000 + AFTER_FINISH_MS)
    rows = len(replay.drivers)
    height = TOP + rows * ROW_HEIGHT + BOTTOM
    return ReplayLayout(VIEWPORT, PX_PER_SECOND, ROW_HEIGHT, TOP, rows, height, duration)


def replay_payload(replay: Replay) -> JsonObject:
    styles = line_styles(replay.drivers)
    winner = race_winner(replay)
    return {
        "total_laps": replay.total_laps,
        "fastest_laps": [[event.at_ms, event.driver_id] for event in replay.fastest_laps],
        "drivers": [
            {
                "driver_id": driver.driver_id,
                "code": driver.label,
                "team": team_name(driver.team),
                "color": styles[driver.driver_id].color,
                "dashed": styles[driver.driver_id].dashed,
                "grid": driver.grid,
                "classified": driver.classified,
                "finish": finish_label(driver, winner, replay),
                "keyframes": [
                    [frame.at_ms, frame.distance, frame.in_pit] for frame in driver.keyframes
                ],
            }
            for driver in replay.drivers
        ],
    }


def race_winner(replay: Replay) -> DriverReplay | None:
    finishers = [
        driver
        for driver in replay.drivers
        if driver.classified and driver.keyframes[-1].distance >= replay.total_laps
    ]
    return min(finishers, key=lambda driver: driver.keyframes[-1].at_ms, default=None)


def finish_label(driver: DriverReplay, winner: DriverReplay | None, replay: Replay) -> str | None:
    if winner is None or not driver.classified:
        return None
    last = driver.keyframes[-1]
    if driver is winner:
        return race_time_text(last.at_ms)
    if last.distance < replay.total_laps:
        return laps_down_text(int(replay.total_laps - last.distance))
    return f"+{(last.at_ms - winner.keyframes[-1].at_ms) / 1000:.3f}"
