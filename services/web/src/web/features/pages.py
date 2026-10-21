from dataclasses import dataclass

from web.entities.chart import Chart, race_chart
from web.entities.errors import NotFound
from web.entities.units import RoundNumber, Season
from web.entities.views import RaceSummary, Trace
from web.features.sources import Analysis, Catalogue


@dataclass(frozen=True, slots=True)
class HomePage:
    seasons: tuple[Season, ...]


@dataclass(frozen=True, slots=True)
class SeasonPage:
    season: Season
    races: tuple[RaceSummary, ...]


@dataclass(frozen=True, slots=True)
class RacePage:
    race: RaceSummary
    trace: Trace
    chart: Chart


def home_page(catalogue: Catalogue) -> HomePage:
    return HomePage(catalogue.seasons())


def season_page(catalogue: Catalogue, season: Season) -> SeasonPage:
    return SeasonPage(season, catalogue.races_of(season))


def race_page(
    catalogue: Catalogue, analysis: Analysis, season: Season, round_number: RoundNumber
) -> RacePage:
    races = {race.round_number: race for race in catalogue.races_of(season)}
    if round_number not in races:
        raise NotFound(f"season {season} has no round {round_number}")
    trace = analysis.trace_of(season, round_number)
    return RacePage(races[round_number], trace, race_chart(trace))
