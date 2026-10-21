from typing import Annotated

from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates

from web.features.sources import Analysis, Catalogue


def get_catalogue(request: Request) -> Catalogue:
    catalogue: Catalogue = request.app.state.catalogue
    return catalogue


def get_analysis(request: Request) -> Analysis:
    analysis: Analysis = request.app.state.analysis
    return analysis


def get_templates(request: Request) -> Jinja2Templates:
    templates: Jinja2Templates = request.app.state.templates
    return templates


CatalogueDep = Annotated[Catalogue, Depends(get_catalogue)]
AnalysisDep = Annotated[Analysis, Depends(get_analysis)]
Templates = Annotated[Jinja2Templates, Depends(get_templates)]
