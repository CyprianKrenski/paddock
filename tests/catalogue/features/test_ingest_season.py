from datetime import date

import pytest

from catalogue.entities.race_snapshot import RaceInfo
from catalogue.entities.units import RoundNumber, Season
from catalogue.features.ingest_season import SeasonNotFound, ingest_season

from tests.catalogue.factories import EnvelopeFactory, ScheduleRaceFactory
from tests.catalogue.fakes import RecordingScheduleStore, ScriptedFetch


def test_schedule_becomes_race_rows_without_total_laps() -> None:
    payload = EnvelopeFactory.build(
        MRData__total="2",
        MRData__RaceTable__Races=[
            ScheduleRaceFactory.build(),
            ScheduleRaceFactory.build(round="2", raceName="Chinese Grand Prix", date="2025-03-23"),
        ],
    )
    fetch = ScriptedFetch({"/2025.json": payload})
    store = RecordingScheduleStore()

    count = ingest_season(fetch, store, season=Season(2025))

    assert count == 2
    assert fetch.calls == [("/2025.json", {"limit": 100, "offset": 0})]
    assert store.saved[0][1] == RaceInfo(
        season=Season(2025),
        round_number=RoundNumber(2),
        name="Chinese Grand Prix",
        circuit_id="albert_park",
        circuit_name="Albert Park Grand Prix Circuit",
        date=date(2025, 3, 23),
        total_laps=None,
    )


def test_unknown_season_raises() -> None:
    fetch = ScriptedFetch({"/1900.json": EnvelopeFactory.build(MRData__total="0")})

    with pytest.raises(SeasonNotFound, match="1900"):
        ingest_season(fetch, RecordingScheduleStore(), season=Season(1900))
