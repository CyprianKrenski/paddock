from typing import Annotated

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from web.api.dependencies import CatalogueDep, LapPath, RoundPath, SeasonPath, Templates
from web.entities.units import Season
from web.features.pages import (
    home_page,
    race_championship,
    race_standings,
    replay_page,
    season_page,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, catalogue: CatalogueDep, templates: Templates) -> HTMLResponse:
    return templates.TemplateResponse(request, "home.html", {"page": home_page(catalogue)})


@router.get("/seasons/{season}", response_class=HTMLResponse)
def show_season(
    request: Request, season: SeasonPath, catalogue: CatalogueDep, templates: Templates
) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "season.html", {"page": season_page(catalogue, season)}
    )


@router.get("/races/{season}/{round_number}/replay", response_class=HTMLResponse)
def show_replay(
    request: Request,
    season: SeasonPath,
    round_number: RoundPath,
    catalogue: CatalogueDep,
    templates: Templates,
) -> HTMLResponse:
    page = replay_page(catalogue, season, round_number)
    return templates.TemplateResponse(request, "replay.html", {"page": page})


@router.get("/races/{season}/{round_number}/standings/{lap}", response_class=HTMLResponse)
def show_standings(
    request: Request,
    season: SeasonPath,
    round_number: RoundPath,
    lap: LapPath,
    catalogue: CatalogueDep,
    templates: Templates,
) -> HTMLResponse:
    standings = race_standings(catalogue, season, round_number, lap)
    return templates.TemplateResponse(request, "standings.html", {"standings": standings})


@router.get("/races/{season}/{round_number}/championship/{lap}", response_class=HTMLResponse)
def show_championship(
    request: Request,
    season: SeasonPath,
    round_number: RoundPath,
    lap: LapPath,
    catalogue: CatalogueDep,
    templates: Templates,
) -> HTMLResponse:
    rows = race_championship(catalogue, season, round_number, lap)
    return templates.TemplateResponse(request, "championship.html", {"rows": rows})


@router.post("/seasons/load")
def load_season(
    season: Annotated[Season, Form(ge=1950, le=2100)], catalogue: CatalogueDep
) -> RedirectResponse:
    catalogue.load_season(season)
    return RedirectResponse(f"/seasons/{season}", status_code=303)


@router.post("/races/{season}/{round_number}/load")
def load_race(
    season: SeasonPath, round_number: RoundPath, catalogue: CatalogueDep
) -> RedirectResponse:
    catalogue.load_race(season, round_number)
    return RedirectResponse(f"/seasons/{season}", status_code=303)
