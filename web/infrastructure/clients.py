import httpx2
from pydantic import TypeAdapter

from web.entities.units import RoundNumber, Season
from web.entities.views import RaceSummary, Replay, StandingBefore, Trace
from web.infrastructure.http import call

SEASONS = TypeAdapter(dict[str, list[Season]])
RACES = TypeAdapter(list[RaceSummary])
STANDINGS = TypeAdapter(list[StandingBefore])
TRACE = TypeAdapter(Trace)
REPLAY = TypeAdapter(Replay)


class HttpCatalogue:
    def __init__(self, http: httpx2.Client, ingest_timeout: float = 180.0) -> None:
        self._http = http
        self._ingest_timeout = ingest_timeout

    def seasons(self) -> tuple[Season, ...]:
        return tuple(SEASONS.validate_python(call(self._http, "GET", "/seasons"))["seasons"])

    def races_of(self, season: Season) -> tuple[RaceSummary, ...]:
        return tuple(RACES.validate_python(call(self._http, "GET", f"/seasons/{season}/races")))

    def load_season(self, season: Season) -> None:
        call(self._http, "POST", f"/seasons/{season}/ingest", self._ingest_timeout)

    def load_race(self, season: Season, round_number: RoundNumber) -> None:
        call(self._http, "POST", f"/races/{season}/{round_number}/ingest", self._ingest_timeout)

    def standings_of(self, season: Season, round_number: RoundNumber) -> tuple[StandingBefore, ...]:
        payload = call(self._http, "GET", f"/seasons/{season}/standings/{round_number}")
        return tuple(STANDINGS.validate_python(payload))

    def trace_of(self, season: Season, round_number: RoundNumber) -> Trace:
        return TRACE.validate_python(
            call(self._http, "GET", f"/races/{season}/{round_number}/trace")
        )

    def replay_of(self, season: Season, round_number: RoundNumber) -> Replay:
        return REPLAY.validate_python(
            call(self._http, "GET", f"/races/{season}/{round_number}/replay")
        )
