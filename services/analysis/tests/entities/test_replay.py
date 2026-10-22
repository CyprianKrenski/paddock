from analysis.entities.replay import Keyframe, driver_keyframes
from analysis.entities.rows import LapRow
from analysis.entities.timeline import RaceTimeline
from analysis.entities.units import Distance, LapNumber, Milliseconds, Position

from analysis_tests.fakes import NORRIS, PIASTRI

TIMELINE = RaceTimeline.from_laps(NORRIS + PIASTRI)
NORRIS_TIMELINE, PIASTRI_TIMELINE = TIMELINE.drivers


def test_a_clean_lap_is_one_keyframe_per_crossing() -> None:
    assert driver_keyframes(NORRIS_TIMELINE, {}) == (
        Keyframe(Milliseconds(0), Distance(0.0), False),
        Keyframe(Milliseconds(117099), Distance(1.0), False),
        Keyframe(Milliseconds(207652), Distance(2.0), False),
    )


def test_a_timed_pit_stop_parks_the_car_just_before_the_line() -> None:
    pits = {LapNumber(2): Milliseconds(20000)}

    assert driver_keyframes(PIASTRI_TIMELINE, pits) == (
        Keyframe(Milliseconds(0), Distance(0.0), False),
        Keyframe(Milliseconds(118000), Distance(1.0), False),
        Keyframe(Milliseconds(188000), Distance(1.97), True),
        Keyframe(Milliseconds(208000), Distance(1.97), True),
        Keyframe(Milliseconds(208000), Distance(2.0), False),
    )


def test_an_untimed_pit_stop_marks_the_whole_lap() -> None:
    pits = {LapNumber(2): None}

    assert driver_keyframes(PIASTRI_TIMELINE, pits) == (
        Keyframe(Milliseconds(0), Distance(0.0), False),
        Keyframe(Milliseconds(118000), Distance(1.0), True),
        Keyframe(Milliseconds(208000), Distance(2.0), False),
    )


def test_a_driver_ends_at_his_last_recorded_crossing_lapped_or_retired() -> None:
    short = RaceTimeline.from_laps(
        (LapRow("x", LapNumber(1), Position(3), Milliseconds(130000)),)
    ).drivers[0]

    assert driver_keyframes(short, {}) == (
        Keyframe(Milliseconds(0), Distance(0.0), False),
        Keyframe(Milliseconds(130000), Distance(1.0), False),
    )


def test_a_pit_stop_longer_than_the_lap_is_capped() -> None:
    pits = {LapNumber(1): Milliseconds(500_000)}

    frames = driver_keyframes(NORRIS_TIMELINE, pits)

    assert frames[1] == Keyframe(Milliseconds(1000), Distance(0.97), True)
