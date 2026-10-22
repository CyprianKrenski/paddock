from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from web.entities.teams import team_color
from web.entities.units import Milliseconds, Position
from web.entities.views import DriverTrace, Trace

VIEWPORT = 960
PX_PER_LAP = 180
HEIGHT = 480
MARGIN_LEFT = VIEWPORT // 2
MARGIN_RIGHT = VIEWPORT // 2
MARGIN_TOP = 32
MARGIN_BOTTOM = 40
GAP_STEPS_SECONDS = (0.5, 1, 2, 5, 10, 20, 30, 60, 120, 300)
MAX_GAP_TICKS = 8


@dataclass(frozen=True, slots=True)
class Tick:
    at: float
    label: str


@dataclass(frozen=True, slots=True)
class ChartPoint:
    x: float
    y: float
    title: str


@dataclass(frozen=True, slots=True)
class ChartLine:
    driver_id: str
    label: str
    color: str
    dashed: bool
    points: str
    dots: tuple[ChartPoint, ...]
    pits: tuple[ChartPoint, ...]


@dataclass(frozen=True, slots=True)
class LineStyle:
    color: str
    dashed: bool


@dataclass(frozen=True, slots=True)
class Marker:
    driver_id: str
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class Chart:
    viewport: int
    width: int
    height: int
    lap_ticks: tuple[Tick, ...]
    gap_ticks: tuple[Tick, ...]
    lines: tuple[ChartLine, ...]
    fastest: Marker | None
    band_x: float
    px_per_lap: int = PX_PER_LAP
    margin_left: int = MARGIN_LEFT


@dataclass(frozen=True, slots=True)
class Scale:
    laps: int
    top_gap: Milliseconds
    step: Milliseconds

    @classmethod
    def for_trace(cls, trace: Trace) -> "Scale":
        max_gap = max((gap for series in trace.series for gap in series.gaps_ms), default=0)
        step = gap_step_ms(max_gap)
        top_gap = Milliseconds(max(step, -(-max_gap // step) * step))
        return cls(max(trace.total_laps, 1), top_gap, step)

    @property
    def width(self) -> int:
        return MARGIN_LEFT + self.laps * PX_PER_LAP + MARGIN_RIGHT

    def x(self, lap: int) -> float:
        return float(MARGIN_LEFT + lap * PX_PER_LAP)

    def y(self, gap_ms: int) -> float:
        plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
        return round(MARGIN_TOP + gap_ms / self.top_gap * plot_height, 1)

    def lap_ticks(self) -> tuple[Tick, ...]:
        return (
            Tick(self.x(0), "Start"),
            *(Tick(self.x(lap), f"L{lap}") for lap in range(1, self.laps)),
            Tick(self.x(self.laps), "Finish"),
        )

    def start_y(self, grid: Position | None, drivers: int) -> float:
        slot = grid - 1 if grid else drivers - 1
        return round(self.y(0) + slot * (HEIGHT - MARGIN_TOP - MARGIN_BOTTOM) / drivers, 1)

    def gap_ticks(self) -> tuple[Tick, ...]:
        return tuple(
            Tick(self.y(gap), f"+{gap / 1000:g}s") for gap in range(0, self.top_gap + 1, self.step)
        )


def gap_step_ms(max_gap_ms: int) -> Milliseconds:
    for seconds in GAP_STEPS_SECONDS:
        if max_gap_ms / (seconds * 1000) <= MAX_GAP_TICKS:
            return Milliseconds(int(seconds * 1000))
    return Milliseconds(GAP_STEPS_SECONDS[-1] * 1000)


class TeamMember(Protocol):
    @property
    def driver_id(self) -> str: ...

    @property
    def team(self) -> str | None: ...


def line_styles(drivers: Iterable[TeamMember]) -> dict[str, LineStyle]:
    seen_teams: set[str | None] = set()
    styles = {}
    for driver in drivers:
        styles[driver.driver_id] = LineStyle(team_color(driver.team), driver.team in seen_teams)
        seen_teams.add(driver.team)
    return styles


def line_for(series: DriverTrace, scale: Scale, style: LineStyle, drivers: int) -> ChartLine:
    label = series.label
    start = ChartPoint(
        scale.x(0),
        scale.start_y(series.grid, drivers),
        f"[{label}] - Grid P{series.grid}\nStart"
        if series.grid
        else f"[{label}] - Pit lane\nStart",
    )
    dots = (
        start,
        *(
            ChartPoint(
                scale.x(lap),
                scale.y(gap),
                f"[{label}] - P{position}\nLap {lap}\n+{gap / 1000:.3f}",
            )
            for lap, (gap, position) in enumerate(
                zip(series.gaps_ms, series.positions, strict=True), start=1
            )
        ),
    )
    pits = tuple(
        ChartPoint(dots[lap].x, dots[lap].y, f"[{label}] pit stop\nLap {lap}")
        for lap in series.pit_laps
        if 0 < lap < len(dots)
    )
    return ChartLine(
        series.driver_id,
        label,
        style.color,
        style.dashed,
        " ".join(f"{dot.x},{dot.y}" for dot in dots),
        dots,
        pits,
    )


def race_chart(trace: Trace) -> Chart:
    scale = Scale.for_trace(trace)
    styles = line_styles(trace.series)
    lines = tuple(
        line_for(series, scale, styles[series.driver_id], len(trace.series))
        for series in trace.series
        if series.positions
    )
    fastest = None
    if trace.fastest_lap is not None:
        gaps = {series.driver_id: series.gaps_ms for series in trace.series}
        gap = gaps[trace.fastest_lap.driver_id][trace.fastest_lap.lap - 1]
        fastest = Marker(trace.fastest_lap.driver_id, scale.x(trace.fastest_lap.lap), scale.y(gap))
    return Chart(
        VIEWPORT,
        scale.width,
        HEIGHT,
        scale.lap_ticks(),
        scale.gap_ticks(),
        lines,
        fastest,
        scale.x(trace.total_laps) - PX_PER_LAP / 2,
    )
