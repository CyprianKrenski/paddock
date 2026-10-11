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
    total = "921"
    RaceTable: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(RaceTableFactory)


class EnvelopeFactory(DictFactory):
    MRData: factory.SubFactory[Any, dict[str, Any]] = factory.SubFactory(MRDataFactory)
