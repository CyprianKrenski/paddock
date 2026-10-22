from dataclasses import dataclass

from web.entities.chart import line_styles
from web.entities.teams import team_name
from web.entities.units import LapNumber, Milliseconds
from web.entities.views import DriverTrace, Trace


@dataclass(frozen=True, slots=True)
class StandingRow:
    rank: int
    code: str
    team: str
    color: str
    dashed: bool
    cell: str
    fastest: bool
    in_pit: bool
    delta: int


@dataclass(frozen=True, slots=True)
class Standings:
    lap: LapNumber
    rows: tuple[StandingRow, ...]


def standings_at(trace: Trace, lap: LapNumber) -> Standings:
    lap = LapNumber(max(0, min(lap, trace.total_laps)))
    styles = line_styles(trace.series)
    fastest = trace.fastest_by_lap[lap - 1].driver_id if lap else None
    rows = tuple(
        StandingRow(
            rank,
            series.label,
            team_name(series.team),
            styles[series.driver_id].color,
            styles[series.driver_id].dashed,
            cell_for(trace, series, lap, leader=rank == 1),
            series.driver_id == fastest,
            lap in series.pit_laps,
            start_position(series, len(trace.series)) - rank,
        )
        for rank, series in enumerate(order_at(trace, lap), start=1)
    )
    return Standings(lap, rows)


def order_at(trace: Trace, lap: LapNumber) -> list[DriverTrace]:
    if lap == 0:
        return sorted(trace.series, key=lambda series: (series.grid in (None, 0), series.grid or 0))
    running = sorted(
        (series for series in trace.series if len(series.positions) >= lap),
        key=lambda series: series.positions[lap - 1],
    )
    behind = sorted(
        (series for series in trace.series if len(series.positions) < lap),
        key=lambda series: (not series.classified, -len(series.positions)),
    )
    return running + behind


def cell_for(trace: Trace, series: DriverTrace, lap: LapNumber, leader: bool) -> str:
    if lap == 0:
        return "START" if leader else ""
    if len(series.positions) < lap:
        return laps_down_text(lap - len(series.positions)) if series.classified else "Out"
    if leader and lap == trace.total_laps and trace.race_time_ms is not None:
        return race_time_text(trace.race_time_ms)
    if leader:
        return f"LAP {lap}"
    if series.laps_down[lap - 1]:
        return laps_down_text(series.laps_down[lap - 1])
    return f"+{series.gaps_ms[lap - 1] / 1000:.3f}"


def laps_down_text(laps: int) -> str:
    return f"+{laps} Lap" if laps == 1 else f"+{laps} Laps"


def race_time_text(time_ms: Milliseconds) -> str:
    hours, rest = divmod(time_ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    seconds = rest / 1000
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:06.3f}"
    return f"{minutes}:{seconds:06.3f}"


def start_position(series: DriverTrace, field: int) -> int:
    return series.grid if series.grid else field
