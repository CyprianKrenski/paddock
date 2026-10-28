import pytest

from web.entities.units import RoundNumber, Season
from web.entities.views import NotFound
from web.features.pages import replay_page

from tests.web.fakes import AUSTRALIA, MemoryCatalogue


def test_replay_page_combines_summary_layout_and_payload() -> None:
    page = replay_page(MemoryCatalogue(), Season(2025), RoundNumber(1))

    assert page.race == AUSTRALIA
    assert page.layout.duration_ms == 213000
    assert [driver["code"] for driver in page.payload["drivers"]] == ["NOR", "PIA", "HAD"]


def test_unknown_round_is_not_found() -> None:
    with pytest.raises(NotFound, match="round 9"):
        replay_page(MemoryCatalogue(), Season(2025), RoundNumber(9))
