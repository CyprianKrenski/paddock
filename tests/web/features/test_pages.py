import pytest

from web.entities.errors import NotFound
from web.entities.units import RoundNumber, Season
from web.features.pages import race_page, season_page

from tests.web.fakes import AUSTRALIA, CHINA, MemoryCatalogue


def test_season_page_lists_races_with_their_status() -> None:
    page = season_page(MemoryCatalogue(), Season(2025))

    assert page.races == (AUSTRALIA, CHINA)


def test_race_page_combines_summary_trace_and_chart() -> None:
    page = race_page(MemoryCatalogue(), Season(2025), RoundNumber(1))

    assert page.race == AUSTRALIA
    assert page.trace.fastest_lap is not None
    assert page.chart.lines[1].driver_id == "piastri"


def test_unknown_round_is_not_found() -> None:
    with pytest.raises(NotFound, match="round 9"):
        race_page(MemoryCatalogue(), Season(2025), RoundNumber(9))
