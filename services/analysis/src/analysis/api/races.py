from typing import Annotated

from fastapi import APIRouter, Query

from analysis.api.dependencies import Source
from analysis.entities.units import RoundNumber, Season
from analysis.features.frame import Frame, build_frame
from analysis.features.trace import Trace, build_trace

router = APIRouter(prefix="/races")


@router.get("/{season}/{round_number}/trace")
def trace(season: Season, round_number: RoundNumber, source: Source) -> Trace:
    return build_trace(source, season, round_number)


@router.get("/{season}/{round_number}/frame")
def frame(
    season: Season, round_number: RoundNumber, source: Source, t: Annotated[float, Query(ge=0)]
) -> Frame:
    return build_frame(source, season, round_number, at_seconds=t)
