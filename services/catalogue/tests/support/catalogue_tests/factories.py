from __future__ import annotations

from typing import TYPE_CHECKING, Any

import factory

if TYPE_CHECKING:
    DictFactory = factory.DictFactory[dict[str, Any]]
else:
    DictFactory = factory.DictFactory


class RaceTableFactory(DictFactory):
    season = "2025"
    round = "1"
    Races: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class MRDataFactory(DictFactory):
    limit = "100"
    offset = "0"
    total = "1"
    RaceTable: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(RaceTableFactory)


class EnvelopeFactory(DictFactory):
    MRData: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(MRDataFactory)


class TimingFactory(DictFactory):
    driverId = "norris"
    position = "1"
    time = "1:57.099"


class LapFactory(DictFactory):
    number = "1"
    Timings: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class RaceFactory(DictFactory):
    season = "2025"
    round = "1"
    raceName = "Australian Grand Prix"
    Laps: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class DriverFactory(DictFactory):
    driverId = "norris"
    code = "NOR"
    givenName = "Lando"
    familyName = "Norris"


class ResultFactory(DictFactory):
    position = "1"
    positionText = "1"
    grid = "1"
    laps = "57"
    status = "Finished"
    Driver: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(DriverFactory)


class ResultsRaceFactory(DictFactory):
    season = "2025"
    round = "1"
    raceName = "Australian Grand Prix"
    Circuit: factory.LazyFunction[dict[str, Any]] = factory.LazyFunction(
        lambda: {"circuitId": "albert_park", "circuitName": "Albert Park Grand Prix Circuit"}
    )
    date = "2025-03-16"
    Results: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class PitStopFactory(DictFactory):
    driverId = "norris"
    lap = "2"
    stop = "1"
    time = "15:22:58"
    duration = "13.341"


class PitStopsRaceFactory(DictFactory):
    season = "2025"
    round = "1"
    PitStops: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)
