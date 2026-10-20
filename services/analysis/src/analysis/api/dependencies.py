from typing import Annotated

from fastapi import Depends, Request

from analysis.features.race_source import RaceSource


def get_source(request: Request) -> RaceSource:
    source: RaceSource = request.app.state.source
    return source


Source = Annotated[RaceSource, Depends(get_source)]
