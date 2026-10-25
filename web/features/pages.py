from dataclasses import dataclass

from web.entities.championship import ChampionshipRow, championship_at
from web.entities.errors import NotFound
from web.entities.json_object import JsonObject
from web.entities.replay import ReplayLayout, replay_layout, replay_payload
from web.entities.standings import Standings, standings_at
from web.entities.units import LapNumber, RoundNumber, Season
from web.entities.views import RaceSummary
from web.features.sources import Catalogue


@dataclass(frozen=True, slots=True)
class HomePage:
    seasons: tuple[Season, ...]


@dataclass(frozen=True, slots=True)
class SeasonPage:
    season: Season
    races: tuple[RaceSummary, ...]


@dataclass(frozen=True, slots=True)
class ReplayPage:
    race: RaceSummary
    layout: ReplayLayout
    payload: JsonObject


def home_page(catalogue: Catalogue) -> HomePage:
    return HomePage(catalogue.seasons())


def season_page(catalogue: Catalogue, season: Season) -> SeasonPage:
    return SeasonPage(season, catalogue.races_of(season))


def race_summary(catalogue: Catalogue, season: Season, round_number: RoundNumber) -> RaceSummary:
    races = {race.round_number: race for race in catalogue.races_of(season)}
    if round_number not in races:
        raise NotFound(f"season {season} has no round {round_number}")
    return races[round_number]


def replay_page(catalogue: Catalogue, season: Season, round_number: RoundNumber) -> ReplayPage:
    race = race_summary(catalogue, season, round_number)
    replay = catalogue.replay_of(season, round_number)
    return ReplayPage(race, replay_layout(replay), replay_payload(replay))


def race_standings(
    catalogue: Catalogue, season: Season, round_number: RoundNumber, lap: LapNumber
) -> Standings:
    return standings_at(catalogue.trace_of(season, round_number), lap)


def race_championship(
    catalogue: Catalogue, season: Season, round_number: RoundNumber, lap: LapNumber
) -> tuple[ChampionshipRow, ...]:
    before = catalogue.standings_of(season, RoundNumber(round_number - 1))
    return championship_at(catalogue.trace_of(season, round_number), before, lap)
