from fastapi.testclient import TestClient

from web.api.dependencies import get_analysis, get_catalogue
from web.entities.errors import UpstreamDown
from web.entities.units import RoundNumber, Season
from web.features.sources import Analysis, Catalogue
from web.main import create_app

from web_tests.fakes import MemoryAnalysis, MemoryCatalogue


def client_with(catalogue: Catalogue, analysis: Analysis | None = None) -> TestClient:
    analysis = analysis or MemoryAnalysis()
    app = create_app()
    app.dependency_overrides[get_catalogue] = lambda: catalogue
    app.dependency_overrides[get_analysis] = lambda: analysis
    return TestClient(app)


def test_home_lists_seasons() -> None:
    response = client_with(MemoryCatalogue()).get("/")

    assert response.status_code == 200
    assert '<a href="/seasons/2025">2025</a>' in response.text


def test_season_page_shows_load_button_only_for_pending_rounds() -> None:
    html = client_with(MemoryCatalogue()).get("/seasons/2025").text

    assert '<a href="/races/2025/1">Australian Grand Prix</a>' in html
    assert 'action="/races/2025/2/load"' in html
    assert 'action="/races/2025/1/load"' not in html


def test_race_page_renders_the_svg_trace_and_fastest_lap() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1").text

    assert "<svg" in html
    assert 'stroke-dasharray="6 4" points="64.0,399.6 244.0,174.0"' in html
    assert "<title>[PIA] - P2\nLap 1\n+0.901</title>" in html
    assert "<title>[PIA] pit stop\nLap 2</title>" in html
    assert 'fill="#ff8000">PIA</text>' in html
    assert "fastest lap <b>piastri</b>" in html


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


def test_frame_api_passes_analysis_json_through() -> None:
    response = client_with(MemoryCatalogue()).get("/api/races/2025/1/frame?t=200")

    assert response.status_code == 200
    assert response.json() == {"at_seconds": 200.0, "drivers": []}


class DeadCatalogue(MemoryCatalogue):
    def seasons(self) -> tuple[Season, ...]:
        raise UpstreamDown("http://catalogue:8000 unreachable: refused")


def test_upstream_down_renders_a_503_page() -> None:
    response = client_with(DeadCatalogue()).get("/")

    assert response.status_code == 503
    assert "unreachable" in response.text
