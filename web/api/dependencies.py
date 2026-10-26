from typing import Annotated

from fastapi import Depends, Path, Request
from fastapi.templating import Jinja2Templates

from web.entities.units import LapNumber, RoundNumber, Season
from web.features.sources import Catalogue


def get_catalogue(request: Request) -> Catalogue:
    catalogue: Catalogue = request.app.state.catalogue
    return catalogue


def get_templates(request: Request) -> Jinja2Templates:
    templates: Jinja2Templates = request.app.state.templates
    return templates


CatalogueDep = Annotated[Catalogue, Depends(get_catalogue)]
Templates = Annotated[Jinja2Templates, Depends(get_templates)]
SeasonPath = Annotated[Season, Path(ge=1950, le=2100)]
RoundPath = Annotated[RoundNumber, Path(ge=1, le=30)]
LapPath = Annotated[LapNumber, Path(ge=0, le=200)]
