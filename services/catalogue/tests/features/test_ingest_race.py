from datetime import date
from typing import Any

import pytest

from catalogue.entities.errors import MalformedSourceRawData
from catalogue.entities.lap_time import LapTimeMs
from catalogue.entities.race_snapshot import (
    DriverInfo,
    LapRow,
    PitStopRow,
    RaceInfo,
    ResultRow,
)
from catalogue.features.ingest_race import IngestSummary, RaceNotFound, ingest_race

from catalogue_tests.factories import (
    DriverFactory,
    EnvelopeFactory,
    LapFactory,
    LapsRaceFactory,
    PitStopFactory,
    PitStopsRaceFactory,
    ResultFactory,
    ResultsRaceFactory,
    TimingFactory,
)
from catalogue_tests.fakes import RecordingStore, ScriptedFetch


def envelope_with(race: dict[str, Any], total: str = "1") -> dict[str, Any]:
    return EnvelopeFactory.build(MRData__total=total, MRData__RaceTable__Races=[race])


def test_ingest_builds_a_snapshot_from_results_laps_and_pit_stops() -> None:
    results = ResultsRaceFactory.build(
        Results=[
            ResultFactory.build(),
            ResultFactory.build(
                position="20",
                grid="11",
                laps="0",
                status="Retired",
                Driver=DriverFactory.build(
                    driverId="hadjar", code="HAD", givenName="Isack", familyName="Hadjar"
                ),
            ),
        ]
    )
    laps = LapsRaceFactory.build(
        Laps=[
            LapFactory.build(number="1", Timings=[TimingFactory.build(time="1:57.099")]),
            LapFactory.build(number="2", Timings=[TimingFactory.build(time="1:30.553")]),
        ]
    )
    pits = PitStopsRaceFactory.build(PitStops=[PitStopFactory.build(duration="13.341")])
    fetch = ScriptedFetch(
        {
            "/2025/1/results.json": envelope_with(results, total="2"),
            "/2025/1/laps.json": envelope_with(laps, total="2"),
            "/2025/1/pitstops.json": envelope_with(pits),
        }
    )
    store = RecordingStore()

    summary = ingest_race(fetch, store, season=2025, round_number=1)

    assert summary == IngestSummary(drivers=2, laps=2, pit_stops=1)
    snapshot = store.saved[0]
    assert snapshot.race == RaceInfo(
        season=2025,
        round_number=1,
        name="Australian Grand Prix",
        circuit_id="albert_park",
        circuit_name="Albert Park Grand Prix Circuit",
        date=date(2025, 3, 16),
        total_laps=57,
    )
    assert snapshot.drivers == (
        DriverInfo(id="norris", code="NOR", given_name="Lando", family_name="Norris"),
        DriverInfo(id="hadjar", code="HAD", given_name="Isack", family_name="Hadjar"),
    )
    assert snapshot.results == (
        ResultRow(driver_id="norris", position=1, grid=1, laps=57, status="Finished"),
        ResultRow(driver_id="hadjar", position=20, grid=11, laps=0, status="Retired"),
    )
    assert snapshot.laps == (
        LapRow(driver_id="norris", lap=1, position=1, time_ms=LapTimeMs(117099)),
        LapRow(driver_id="norris", lap=2, position=1, time_ms=LapTimeMs(90553)),
    )
    assert snapshot.pit_stops == (
        PitStopRow(driver_id="norris", stop=1, lap=2, duration_ms=LapTimeMs(13341)),
    )


def test_unknown_round_raises_race_not_found_and_saves_nothing() -> None:
    fetch = ScriptedFetch({"/2025/99/results.json": EnvelopeFactory.build(MRData__total="0")})
    store = RecordingStore()

    with pytest.raises(RaceNotFound, match="2025 round 99"):
        ingest_race(fetch, store, season=2025, round_number=99)

    assert store.saved == []


def test_lap_for_a_driver_missing_from_results_is_malformed_source_data() -> None:
    results = ResultsRaceFactory.build(Results=[ResultFactory.build()])
    laps = LapsRaceFactory.build(
        Laps=[LapFactory.build(Timings=[TimingFactory.build(driverId="ghost")])]
    )
    fetch = ScriptedFetch(
        {
            "/2025/1/results.json": envelope_with(results),
            "/2025/1/laps.json": envelope_with(laps),
            "/2025/1/pitstops.json": EnvelopeFactory.build(MRData__total="0"),
        }
    )

    with pytest.raises(MalformedSourceRawData, match="ghost"):
        ingest_race(fetch, RecordingStore(), season=2025, round_number=1)
