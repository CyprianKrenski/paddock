from analysis.entities.frame import DriverState, replay_frame
from analysis.entities.rows import LapRow, ResultRow
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


def test_lapped_drivers_are_classified_as_finished() -> None:
    lapped = {
        **BY_DRIVER,
        "piastri": ResultRow(
            "piastri", "PIA", "mclaren", Position(2), Position(2), LapNumber(1), "Lapped"
        ),
    }
    one_lap = (LapRow("piastri", LapNumber(1), Position(2), Milliseconds(118000)),)

    frame = replay_frame(
        RaceTimeline.from_laps(NORRIS + one_lap), lapped, at_ms=Milliseconds(999_999)
    )

    assert frame[1] == DriverState(
        "piastri", Position(2), LapNumber(1), Distance(1.0), None, DriverStatus.FINISHED
    )


def test_a_driver_without_laps_is_out_from_the_start() -> None:
    timeline = RaceTimeline.from_laps(NORRIS + PIASTRI, driver_ids=BY_DRIVER)

    frame = replay_frame(timeline, BY_DRIVER, at_ms=Milliseconds(0))

    assert frame[2] == DriverState(
        "hadjar", Position(3), LapNumber(0), Distance(0.0), None, DriverStatus.OUT
    )


def test_a_retired_driver_ranks_behind_everyone_still_running() -> None:
    retired = (LapRow("hadjar", LapNumber(1), Position(1), Milliseconds(100000)),)

    frame = replay_frame(
        RaceTimeline.from_laps(NORRIS + PIASTRI + retired), BY_DRIVER, at_ms=Milliseconds(100_000)
    )

    assert [(state.driver_id, state.status) for state in frame] == [
        ("norris", DriverStatus.RUNNING),
        ("piastri", DriverStatus.RUNNING),
        ("hadjar", DriverStatus.OUT),
    ]


def test_the_start_frame_is_ordered_by_grid() -> None:
    swapped = {
        "norris": ResultRow(
            "norris", "NOR", "mclaren", Position(1), Position(2), LapNumber(2), "Finished"
        ),
        "piastri": ResultRow(
            "piastri", "PIA", "mclaren", Position(2), Position(1), LapNumber(2), "Finished"
        ),
    }

    frame = replay_frame(RaceTimeline.from_laps(NORRIS + PIASTRI), swapped, at_ms=Milliseconds(0))

    assert [state.driver_id for state in frame] == ["piastri", "norris"]
