import logging

import pytest
from fastapi.testclient import TestClient

from web.api.dependencies import get_catalogue
from web.entities.units import RoundNumber, Season
from web.entities.views import UpstreamDown
from web.features.sources import Catalogue
from web.main import create_app

from tests.web.fakes import MemoryCatalogue


def client_with(catalogue: Catalogue) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_catalogue] = lambda: catalogue
    return TestClient(app)


def test_home_lists_seasons() -> None:
    response = client_with(MemoryCatalogue()).get("/")

    assert response.status_code == 200
    assert '<a href="/seasons/2025">2025</a>' in response.text


def test_season_page_links_to_the_replay_and_offers_load_only_for_pending_rounds() -> None:
    html = client_with(MemoryCatalogue()).get("/seasons/2025").text

    assert '<a href="/races/2025/1/replay">Australian Grand Prix</a>' in html
    assert 'href="/races/2025/1"' not in html
    assert 'action="/races/2025/2/load"' in html
    assert 'action="/races/2025/1/load"' not in html


def test_load_race_posts_to_catalogue_then_redirects_to_the_season() -> None:
    catalogue = MemoryCatalogue()

    response = client_with(catalogue).post("/races/2025/2/load", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/seasons/2025"
    assert catalogue.loaded == [(Season(2025), RoundNumber(2))]


def test_load_season_reads_the_form_field_then_redirects() -> None:
    catalogue = MemoryCatalogue()

    response = client_with(catalogue).post(
        "/seasons/load", data={"season": "2024"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/seasons/2024"
    assert catalogue.loaded == [(Season(2024), None)]


def test_home_form_posts_to_a_fixed_action_without_javascript() -> None:
    html = client_with(MemoryCatalogue()).get("/").text

    assert '<form method="post" action="/seasons/load">' in html
    assert "onsubmit" not in html


class DeadCatalogue(MemoryCatalogue):
    def seasons(self) -> tuple[Season, ...]:
        raise UpstreamDown("http://catalogue:8000 unreachable: refused")


def test_upstream_down_renders_a_503_page_without_the_upstream_address(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING):
        response = client_with(DeadCatalogue()).get("/")

    assert response.status_code == 503
    assert "unavailable" in response.text
    assert "catalogue:8000" not in response.text
    assert "http://catalogue:8000 unreachable: refused" in caplog.text


def test_api_docs_are_not_served_by_web() -> None:
    client = client_with(MemoryCatalogue())

    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_out_of_range_path_parameters_are_rejected_before_any_upstream_call() -> None:
    client = client_with(DeadCatalogue())

    assert client.get("/races/1800/1/replay").status_code == 422
    assert client.get("/races/2025/0/replay").status_code == 422
    assert client.get("/races/2025/1/standings/999").status_code == 422
    assert client.post("/seasons/load", data={"season": "1800"}).status_code == 422


def test_standings_fragment_renders_rows_for_the_requested_lap() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1/standings/1").text

    assert html.count("<tr") == 2
    assert "<td>LAP 1</td>" in html
    assert "<td>+0.901</td>" in html
    assert html.count("fastest lap") == 1
    assert "In Pit" not in html


def test_standings_at_the_start_follow_the_grid() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1/standings/0").text

    assert html.index("<b>PIA</b>") < html.index("<b>NOR</b>")
    assert "<td>START</td>" in html
    assert "fastest lap" not in html


def test_replay_page_embeds_keyframes_and_the_script() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1/replay").text

    assert '<script type="application/json" id="replay-data">' in html
    assert '"keyframes": [[0, 0.0, false], [117099, 1.0, false], [207652, 2.0, false]]' in html
    assert 'data-standings-url="/races/2025/1/standings"' in html
    assert 'data-championship-url="/races/2025/1/championship"' in html
    assert '<input type="range" id="time" min="0" max="213000"' in html
    assert ">P3</text>" in html
    assert 'id="moment"' in html and 'id="chequered"' in html
    assert '<button type="button" data-mode="championship">' in html
    assert '<button type="button" id="play">Play</button>' in html
    assert '<option value="120" selected>120x</option>' in html
    assert "1x" not in html.split("<select")[1].split("</select>")[0]
    assert "r.ok ? r.text()" in html


def test_pages_carry_breadcrumbs_back_to_the_seasons() -> None:
    client = client_with(MemoryCatalogue())

    season = client.get("/seasons/2025").text
    replay = client.get("/races/2025/1/replay").text

    assert '<a href="/" class="crumb">Seasons</a>' in season
    assert '<a href="/seasons/2025" class="crumb">Season 2025</a>' in replay
    assert "race trace</a>" not in replay


def test_championship_fragment_projects_points_for_the_lap() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/2/championship/2").text

    assert html.count("<tr") == 4
    assert '<td>50 <span class="gained">+25</span></td>' in html
    assert html.count('<span class="gain">+1</span>') == 2
    assert '<span class="loss">-2</span>' in html
    assert html.count('<span class="same">&ndash;</span>') == 1
    assert "<b>HAD</b>" in html and "<b>LAW</b>" in html


def test_standings_fragment_shows_places_gained_since_the_grid() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1/standings/2").text

    assert html.count('<span class="gain">+1</span>') == 1
    assert html.count('<span class="loss">-1</span>') == 1
    assert '<span class="same">&ndash;</span>' not in html
