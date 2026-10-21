from dataclasses import dataclass

from web.entities.teams import team_color
from web.entities.units import Milliseconds
from web.entities.views import DriverTrace, Trace

VIEWPORT = 960
PX_PER_LAP = 180
HEIGHT = 480
MARGIN_LEFT = 64
MARGIN_RIGHT = 80
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
    label_x: float
    label_y: float


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
        return MARGIN_LEFT + (self.laps - 1) * PX_PER_LAP + MARGIN_RIGHT

    def x(self, lap: int) -> float:
        return float(MARGIN_LEFT + (lap - 1) * PX_PER_LAP)

    def y(self, gap_ms: int) -> float:
        plot_height = HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
        return round(MARGIN_TOP + gap_ms / self.top_gap * plot_height, 1)

    def lap_ticks(self) -> tuple[Tick, ...]:
        return tuple(Tick(self.x(lap), str(lap)) for lap in range(1, self.laps + 1))

    def gap_ticks(self) -> tuple[Tick, ...]:
        return tuple(
            Tick(self.y(gap), f"+{gap / 1000:g}s") for gap in range(0, self.top_gap + 1, self.step)
        )


def gap_step_ms(max_gap_ms: int) -> Milliseconds:
    for seconds in GAP_STEPS_SECONDS:
        if max_gap_ms / (seconds * 1000) <= MAX_GAP_TICKS:
            return Milliseconds(int(seconds * 1000))
    return Milliseconds(GAP_STEPS_SECONDS[-1] * 1000)


def line_for(series: DriverTrace, scale: Scale, dashed: bool) -> ChartLine:
    label = series.code or series.driver_id[:3].upper()
    dots = tuple(
        ChartPoint(
            scale.x(lap), scale.y(gap), f"[{label}] - P{position}\nLap {lap}\n+{gap / 1000:.3f}"
        )
        for lap, (gap, position) in enumerate(
            zip(series.gaps_ms, series.positions, strict=True), start=1
        )
    )
    pits = tuple(
        ChartPoint(dots[lap - 1].x, dots[lap - 1].y, f"[{label}] pit stop\nLap {lap}")
        for lap in series.pit_laps
        if 0 < lap <= len(dots)
    )
    last = dots[-1] if dots else ChartPoint(scale.x(1), scale.y(0), "")
    return ChartLine(
        series.driver_id,
        label,
        team_color(series.team),
        dashed,
        " ".join(f"{dot.x},{dot.y}" for dot in dots),
        dots,
        pits,
        last.x + 8,
        last.y + 4,
    )


def race_chart(trace: Trace) -> Chart:
    scale = Scale.for_trace(trace)
    seen_teams: set[str | None] = set()
    lines = []
    for series in trace.series:
        lines.append(line_for(series, scale, dashed=series.team in seen_teams))
        seen_teams.add(series.team)
    fastest = None
    if trace.fastest_lap is not None:
        gaps = {series.driver_id: series.gaps_ms for series in trace.series}
        gap = gaps[trace.fastest_lap.driver_id][trace.fastest_lap.lap - 1]
        fastest = Marker(trace.fastest_lap.driver_id, scale.x(trace.fastest_lap.lap), scale.y(gap))
    return Chart(
        VIEWPORT, scale.width, HEIGHT, scale.lap_ticks(), scale.gap_ticks(), tuple(lines), fastest
    )
