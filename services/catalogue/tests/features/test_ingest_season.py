from collections.abc import Mapping
from datetime import date
from typing import Any

import pytest

from catalogue.entities.race_snapshot import RaceInfo
from catalogue.features.ingest_season import SeasonNotFound, ingest_season

from catalogue_tests.factories import EnvelopeFactory, ScheduleRaceFactory


class RecordingScheduleStore:
    def __init__(self) -> None:
        self.saved: list[tuple[RaceInfo, ...]] = []

    def save_schedule(self, races: tuple[RaceInfo, ...]) -> None:
        self.saved.append(races)


def fetch_returning(payload: dict[str, Any], expected_path: str) -> Any:
    def fetch(path: str, params: Mapping[str, str | int] | None = None) -> dict[str, Any]:
        assert path == expected_path
        return payload

    return fetch


def test_schedule_becomes_race_rows_without_total_laps() -> None:
    payload = EnvelopeFactory.build(
        MRData__total="2",
        MRData__RaceTable__Races=[
            ScheduleRaceFactory.build(),
            ScheduleRaceFactory.build(round="2", raceName="Chinese Grand Prix", date="2025-03-23"),
        ],
    )
    store = RecordingScheduleStore()

    count = ingest_season(fetch_returning(payload, "/2025.json"), store, season=2025)

    assert count == 2
    assert store.saved[0][1] == RaceInfo(
        season=2025,
        round_number=2,
        name="Chinese Grand Prix",
        circuit_id="albert_park",
        circuit_name="Albert Park Grand Prix Circuit",
        date=date(2025, 3, 23),
        total_laps=None,
    )


def test_unknown_season_raises() -> None:
    with pytest.raises(SeasonNotFound, match="1900"):
        ingest_season(
            fetch_returning(EnvelopeFactory.build(MRData__total="0"), "/1900.json"),
            RecordingScheduleStore(),
            season=1900,
        )
