import pytest
from pydantic import ValidationError

from catalogue.infrastructure.jolpica_pages import LapTiming, fetch_lap_timings, pages

from catalogue_tests.factories import EnvelopeFactory, LapFactory, LapsRaceFactory, TimingFactory
from catalogue_tests.fakes import ScriptedFetch


def test_pages_walk_offsets_until_total() -> None:
    fetch = ScriptedFetch(
        responses=[
            EnvelopeFactory.build(MRData__total="250", MRData__offset=str(o)) for o in (0, 100, 200)
        ]
    )

    offsets = [page["MRData"]["offset"] for page in pages(fetch, "/2025/1/laps.json")]

    assert offsets == ["0", "100", "200"]
    assert fetch.calls == [
        ("/2025/1/laps.json", {"limit": 100, "offset": 0}),
        ("/2025/1/laps.json", {"limit": 100, "offset": 100}),
        ("/2025/1/laps.json", {"limit": 100, "offset": 200}),
    ]


@pytest.mark.parametrize(("total", "calls"), [("0", 1), ("50", 1), ("200", 2), ("201", 3)])
def test_pages_request_count_follows_total(total: str, calls: int) -> None:
    fetch = ScriptedFetch(responses=[EnvelopeFactory.build(MRData__total=total)] * 3)

    list(pages(fetch, "/2025/1/laps.json"))

    assert len(fetch.calls) == calls


def test_unknown_round_yields_no_timings_instead_of_an_error() -> None:
    fetch = ScriptedFetch(responses=[EnvelopeFactory.build(MRData__total="0")])

    assert list(fetch_lap_timings(fetch, season=2025, round_number=99)) == []


def test_lap_timings_flatten_a_lap_split_across_pages() -> None:
    first_page = EnvelopeFactory.build(
        MRData__total="3",
        MRData__limit="2",
        MRData__RaceTable__Races=[
            LapsRaceFactory.build(
                Laps=[
                    LapFactory.build(
                        number="6",
                        Timings=[
                            TimingFactory.build(),
                            TimingFactory.build(driverId="piastri", position="2", time="1:58.000"),
                        ],
                    )
                ]
            )
        ],
    )
    second_page = EnvelopeFactory.build(
        MRData__total="3",
        MRData__limit="2",
        MRData__offset="2",
        MRData__RaceTable__Races=[
            LapsRaceFactory.build(
                Laps=[
                    LapFactory.build(
                        number="6",
                        Timings=[
                            TimingFactory.build(driverId="leclerc", position="3", time="2:00.500")
                        ],
                    )
                ]
            )
        ],
    )

    timings = list(
        fetch_lap_timings(
            ScriptedFetch(responses=[first_page, second_page]), season=2025, round_number=1
        )
    )

    assert timings == [
        LapTiming(lap=6, driver_id="norris", position=1, time="1:57.099"),
        LapTiming(lap=6, driver_id="piastri", position=2, time="1:58.000"),
        LapTiming(lap=6, driver_id="leclerc", position=3, time="2:00.500"),
    ]


def test_unexpected_payload_is_a_validation_error() -> None:
    with pytest.raises(ValidationError):
        list(
            fetch_lap_timings(
                ScriptedFetch(responses=[{"MRData": {"total": "1"}}]), season=2025, round_number=1
            )
        )


def test_zero_limit_cannot_loop_forever() -> None:
    fetch = ScriptedFetch(
        responses=[EnvelopeFactory.build(MRData__total="921", MRData__limit="0")] * 3
    )

    with pytest.raises(ValidationError, match="limit"):
        list(pages(fetch, "/2025/1/laps.json"))

    assert len(fetch.calls) == 1
