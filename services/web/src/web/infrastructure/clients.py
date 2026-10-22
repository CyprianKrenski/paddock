import httpx2
from pydantic import TypeAdapter

from web.entities.json_object import JsonObject
from web.entities.units import RoundNumber, Season
from web.entities.views import RaceSummary, Replay, StandingBefore, Trace
from web.infrastructure.http import call

SEASONS = TypeAdapter(dict[str, list[Season]])
RACES = TypeAdapter(list[RaceSummary])
STANDINGS = TypeAdapter(list[StandingBefore])
TRACE = TypeAdapter(Trace)
REPLAY = TypeAdapter(Replay)
FRAME = TypeAdapter(JsonObject)


class HttpCatalogue:
    def __init__(self, http: httpx2.Client) -> None:
        self._http = http

    def seasons(self) -> tuple[Season, ...]:
        return tuple(SEASONS.validate_python(call(self._http, "GET", "/seasons"))["seasons"])

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        return tuple(RACES.validate_python(call(self._http, "GET", f"/seasons/{season}/races")))

    def load_season(self, season: Season) -> None:
        call(self._http, "POST", f"/seasons/{season}/ingest")

    def load_race(self, season: Season, round_number: RoundNumber) -> None:
        call(self._http, "POST", f"/races/{season}/{round_number}/ingest")

    def standings_of(self, season: Season, round_number: RoundNumber) -> tuple[StandingBefore, ...]:
        payload = call(self._http, "GET", f"/seasons/{season}/standings/{round_number}")
        return tuple(STANDINGS.validate_python(payload))


class HttpAnalysis:
    def __init__(self, http: httpx2.Client) -> None:
        self._http = http

    def trace_of(self, season: Season, round_number: RoundNumber) -> Trace:
        return TRACE.validate_python(
            call(self._http, "GET", f"/races/{season}/{round_number}/trace")
        )

    def frame_of(self, season: Season, round_number: RoundNumber, at_seconds: float) -> JsonObject:
        payload = call(self._http, "GET", f"/races/{season}/{round_number}/frame", t=at_seconds)
        return FRAME.validate_python(payload)

    def replay_of(self, season: Season, round_number: RoundNumber) -> Replay:
        return REPLAY.validate_python(
            call(self._http, "GET", f"/races/{season}/{round_number}/replay")
        )
