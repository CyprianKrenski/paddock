from dataclasses import replace

from web.entities.chart import ChartPoint, Marker, Scale, Tick, gap_step_ms, race_chart
from web.entities.teams import team_color
from web.entities.units import Milliseconds, Position
from web.entities.views import DriverTrace

from web_tests.fakes import TRACE


def test_chart_is_panoramic_with_a_lap_grid_and_a_nice_gap_scale() -> None:
    chart = race_chart(TRACE)

    assert chart.viewport == 960
    assert chart.width == 480 + 2 * 180 + 480
    assert chart.lap_ticks == (Tick(480.0, "Start"), Tick(660.0, "L1"), Tick(840.0, "Finish"))
    assert chart.gap_ticks == (Tick(32.0, "+0s"), Tick(236.0, "+0.5s"), Tick(440.0, "+1s"))


def test_lines_use_team_colours_dashes_for_teammates_and_hover_titles() -> None:
    chart = race_chart(TRACE)

    norris, piastri = chart.lines
    assert (norris.label, norris.color, norris.dashed) == ("NOR", "#ff8000", False)
    assert (piastri.label, piastri.color, piastri.dashed) == ("PIA", "#ff8000", True)
    assert norris.points == "480.0,236.0 660.0,32.0 840.0,32.0"
    assert piastri.points == "480.0,32.0 660.0,399.6 840.0,174.0"
    assert piastri.dots[0] == ChartPoint(480.0, 32.0, "[PIA] - Grid P1\nStart")
    assert piastri.dots[1] == ChartPoint(660.0, 399.6, "[PIA] - P2\nLap 1\n+0.901")
    assert piastri.pits == (ChartPoint(840.0, 174.0, "[PIA] pit stop\nLap 2"),)
    assert chart.fastest == Marker("piastri", 840.0, 174.0)
    assert (chart.band_x, chart.px_per_lap, chart.margin_left) == (750.0, 180, 480)


def test_gap_step_grows_with_the_spread() -> None:
    assert gap_step_ms(901) == 500
    assert gap_step_ms(30_000) == 5_000
    assert gap_step_ms(95_000) == 20_000


def test_unknown_teams_get_a_stable_fallback_colour() -> None:
    assert team_color("ferrari") == "#e8002d"
    assert team_color("hesketh") == team_color("hesketh")
    assert team_color("hesketh") != team_color(None)


def test_scale_maps_laps_and_gaps_independently_of_the_trace() -> None:
    scale = Scale(laps=53, top_gap=Milliseconds(120_000), step=Milliseconds(20_000))

    assert scale.width == 480 + 53 * 180 + 480
    assert (scale.x(0), scale.x(53)) == (480.0, 10020.0)
    assert (scale.y(0), scale.y(120_000)) == (32.0, 440.0)
    assert len(scale.gap_ticks()) == 7


def test_a_driver_without_laps_draws_no_line() -> None:
    trace = replace(
        TRACE,
        series=TRACE.series
        + (DriverTrace("hadjar", "HAD", "rb", Position(11), False, (), (), (), ()),),
    )

    assert [line.label for line in race_chart(trace).lines] == ["NOR", "PIA"]
