from web.entities.replay import ReplayLayout, replay_layout, replay_payload
from web.entities.units import Milliseconds, RoundNumber, Season
from web.features.pages import replay_page

from tests.web.fakes import AUSTRALIA, REPLAY, MemoryCatalogue


def test_layout_spans_the_race_duration() -> None:
    assert replay_layout(REPLAY) == ReplayLayout(
        viewport=960,
        px_per_second=4,
        row_height=24,
        top=28,
        rows=3,
        height=28 + 3 * 24 + 36,
        duration_ms=Milliseconds(213000),
    )


def test_payload_is_plain_json_with_styles_keyframes_and_finish_labels() -> None:
    payload = replay_payload(REPLAY)

    assert payload["total_laps"] == 2
    assert payload["fastest_laps"] == [[117099, "norris"], [208000, "piastri"]]
    assert payload["drivers"][1] == {
        "driver_id": "piastri",
        "code": "PIA",
        "team": "McLaren",
        "color": "#ff8000",
        "dashed": True,
        "grid": 1,
        "classified": True,
        "finish": "+0.348",
        "keyframes": [
            [0, 0.0, False],
            [118000, 1.0, False],
            [194659, 1.97, True],
            [208000, 1.97, True],
            [208000, 2.0, False],
        ],
    }
    assert payload["drivers"][0]["finish"] == "3:27.652"
    assert payload["drivers"][2]["finish"] is None


def test_replay_page_combines_race_summary_layout_and_payload() -> None:
    page = replay_page(MemoryCatalogue(), Season(2025), RoundNumber(1))

    assert page.race == AUSTRALIA
    assert page.layout.duration_ms == 213000
    assert [driver["code"] for driver in page.payload["drivers"]] == ["NOR", "PIA", "HAD"]
