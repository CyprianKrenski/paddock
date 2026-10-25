import pytest

from web.entities.errors import NotFound
from web.entities.units import RoundNumber, Season
from web.features.pages import replay_page, season_page

from tests.web.fakes import AUSTRALIA, CHINA, MemoryCatalogue


def test_season_page_lists_races_with_their_status() -> None:
    page = season_page(MemoryCatalogue(), Season(2025))

    assert page.races == (AUSTRALIA, CHINA)


def test_replay_page_combines_summary_and_keyframes() -> None:
    page = replay_page(MemoryCatalogue(), Season(2025), RoundNumber(1))

    assert page.race == AUSTRALIA
    assert page.payload["drivers"][0]["code"] == "NOR"
    assert page.payload["fastest_laps"] == [[117099, "norris"], [208000, "piastri"]]


def test_unknown_round_is_not_found() -> None:
    with pytest.raises(NotFound, match="round 9"):
        replay_page(MemoryCatalogue(), Season(2025), RoundNumber(9))
