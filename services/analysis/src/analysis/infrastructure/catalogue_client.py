import httpx2
from pydantic import TypeAdapter

from analysis.entities.errors import CatalogueUnavailable, RaceNotAvailable
from analysis.entities.rows import LapRow, PitStopRow, ResultRow
from analysis.entities.units import RoundNumber, Season

LAPS = TypeAdapter(list[LapRow])
RESULTS = TypeAdapter(list[ResultRow])
PIT_STOPS = TypeAdapter(list[PitStopRow])


class HttpCatalogue:
    def __init__(self, http: httpx2.Client) -> None:
        self._http = http

    def laps_of(self, season: Season, round_number: RoundNumber) -> tuple[LapRow, ...]:
        return tuple(LAPS.validate_python(self._get(f"/races/{season}/{round_number}/laps")))

    def results_of(self, season: Season, round_number: RoundNumber) -> tuple[ResultRow, ...]:
        return tuple(RESULTS.validate_python(self._get(f"/races/{season}/{round_number}/results")))

    def pit_stops_of(self, season: Season, round_number: RoundNumber) -> tuple[PitStopRow, ...]:
        payload = self._get(f"/races/{season}/{round_number}/pit-stops")
        return tuple(PIT_STOPS.validate_python(payload))

    def _get(self, path: str) -> object:
        try:
            response = self._http.get(path)
        except httpx2.TransportError as error:
            raise CatalogueUnavailable(f"catalogue unreachable: {error}") from error
        if response.status_code == 404:
            raise RaceNotAvailable(response.json().get("detail", path))
        if response.status_code != 200:
            raise CatalogueUnavailable(f"catalogue answered {response.status_code} for {path}")
        return response.json()
