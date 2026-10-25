import pytest
from pydantic import ValidationError

from catalogue.entities.units import LapNumber, Position, RoundNumber, Season
from catalogue.infrastructure.jolpica_pages import (
    LapTiming,
    fetch_driver_standings,
    fetch_lap_timings,
    pages,
)

from tests.catalogue.factories import (
    EnvelopeFactory,
    LapFactory,
    LapsRaceFactory,
    StandingFactory,
    StandingsEnvelopeFactory,
    StandingsListFactory,
    TimingFactory,
)
from tests.catalogue.fakes import ScriptedFetch


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

    assert list(fetch_lap_timings(fetch, season=Season(2025), round_number=RoundNumber(99))) == []


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
            ScriptedFetch(responses=[first_page, second_page]),
            season=Season(2025),
            round_number=RoundNumber(1),
        )
    )

    assert timings == [
        LapTiming(lap=LapNumber(6), driver_id="norris", position=Position(1), time="1:57.099"),
        LapTiming(lap=LapNumber(6), driver_id="piastri", position=Position(2), time="1:58.000"),
        LapTiming(lap=LapNumber(6), driver_id="leclerc", position=Position(3), time="2:00.500"),
    ]


def test_unexpected_payload_is_a_validation_error() -> None:
    with pytest.raises(ValidationError):
        list(
            fetch_lap_timings(
                ScriptedFetch(responses=[{"MRData": {"total": "1"}}]),
                season=Season(2025),
                round_number=RoundNumber(1),
            )
        )


def test_zero_limit_cannot_loop_forever() -> None:
    fetch = ScriptedFetch(
        responses=[EnvelopeFactory.build(MRData__total="921", MRData__limit="0")] * 3
    )

    with pytest.raises(ValidationError, match="limit"):
        list(pages(fetch, "/2025/1/laps.json"))

    assert len(fetch.calls) == 1


def test_driver_standings_are_read_from_the_standings_table() -> None:
    standings = StandingsListFactory.build(
        DriverStandings=[
            StandingFactory.build(),
            StandingFactory.build(
                position="2",
                points="28.5",
                wins="0",
                Driver={
                    "driverId": "piastri",
                    "code": "PIA",
                    "givenName": "Oscar",
                    "familyName": "Piastri",
                },
            ),
        ]
    )
    fetch = ScriptedFetch(
        {
            "/2025/2/driverStandings.json": StandingsEnvelopeFactory.build(
                MRData__StandingsTable__StandingsLists=[standings]
            )
        }
    )

    entries = fetch_driver_standings(fetch, Season(2025), RoundNumber(2))

    assert [(e.driver.driver_id, e.position, e.points, e.wins) for e in entries] == [
        ("norris", 1, 44.0, 1),
        ("piastri", 2, 28.5, 0),
    ]


def test_standings_before_the_first_round_are_empty() -> None:
    fetch = ScriptedFetch(
        {"/2025/0/driverStandings.json": StandingsEnvelopeFactory.build(MRData__total="0")}
    )

    assert fetch_driver_standings(fetch, Season(2025), RoundNumber(0)) == []
