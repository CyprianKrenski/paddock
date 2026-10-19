from __future__ import annotations

from typing import TYPE_CHECKING, Any

import factory

if TYPE_CHECKING:
    DictFactory = factory.DictFactory[dict[str, Any]]
else:
    DictFactory = factory.DictFactory


class RaceTableFactory(DictFactory):
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


class LapsRaceFactory(DictFactory):
    Laps: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class CircuitFactory(DictFactory):
    circuitId = "albert_park"
    circuitName = "Albert Park Grand Prix Circuit"


class DriverFactory(DictFactory):
    driverId = "norris"
    code = "NOR"
    givenName = "Lando"
    familyName = "Norris"


class ResultFactory(DictFactory):
    position = "1"
    grid = "1"
    laps = "57"
    status = "Finished"
    Driver: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(DriverFactory)


class ResultsRaceFactory(DictFactory):
    season = "2025"
    round = "1"
    raceName = "Australian Grand Prix"
    Circuit: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(CircuitFactory)
    date = "2025-03-16"
    Results: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class PitStopFactory(DictFactory):
    driverId = "norris"
    lap = "2"
    stop = "1"
    duration = "13.341"


class PitStopsRaceFactory(DictFactory):
    PitStops: factory.LazyFunction[list[Any]] = factory.LazyFunction(list)


class ScheduleRaceFactory(DictFactory):
    season = "2025"
    round = "1"
    raceName = "Australian Grand Prix"
    Circuit: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(CircuitFactory)
    date = "2025-03-16"
