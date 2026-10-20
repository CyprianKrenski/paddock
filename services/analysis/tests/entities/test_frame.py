from analysis.entities.frame import DriverState, replay_frame
from analysis.entities.rows import LapRow
from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import Distance, DriverStatus, LapNumber, Milliseconds, Position

from analysis_tests.fakes import NORRIS, PIASTRI, RESULTS

BY_DRIVER = {row.driver_id: row for row in RESULTS}


def test_mid_race_frame_interpolates_inside_the_current_lap() -> None:
    frame = replay_frame(
        RaceTimeline.from_laps(NORRIS + PIASTRI), BY_DRIVER, at_ms=Milliseconds(200_000)
    )

    assert frame == (
        DriverState(
            "norris",
            Position(1),
            LapNumber(1),
            Distance(1 + 82901 / 90553),
            Milliseconds(0),
            DriverStatus.RUNNING,
        ),
        DriverState(
            "piastri",
            Position(2),
            LapNumber(1),
            Distance(1 + 82000 / 90000),
            Milliseconds(395),
            DriverStatus.RUNNING,
        ),
    )


def test_after_the_last_crossing_drivers_are_finished_or_out() -> None:
    retired = (LapRow("hadjar", LapNumber(1), Position(3), Milliseconds(130000)),)

    frame = replay_frame(
        RaceTimeline.from_laps(NORRIS + PIASTRI + retired), BY_DRIVER, at_ms=Milliseconds(999_999)
    )

    assert frame == (
        DriverState(
            "norris", Position(1), LapNumber(2), Distance(2.0), None, DriverStatus.FINISHED
        ),
        DriverState(
            "piastri", Position(2), LapNumber(2), Distance(2.0), None, DriverStatus.FINISHED
        ),
        DriverState("hadjar", Position(3), LapNumber(1), Distance(1.0), None, DriverStatus.OUT),
    )
