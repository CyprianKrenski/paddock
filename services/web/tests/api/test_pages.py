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
    assert 'stroke-dasharray="6 4" points="480.0,32.0 660.0,399.6 840.0,174.0"' in html
    assert "<title>[PIA] - P2\nLap 1\n+0.901</title>" in html
    assert "<title>[PIA] pit stop\nLap 2</title>" in html
    assert html.count('fill="#ff8000">PIA</text>') == 3
    assert '<text class="code" x="665.0" y="394.6" fill="#ff8000">PIA</text>' in html
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


def test_race_page_has_a_classification_table_for_the_last_lap() -> None:
    html = client_with(MemoryCatalogue()).get("/races/2025/1").text

    assert '<tbody id="standings" data-lap="2">' in html
    assert 'data-px-per-lap="180"' in html
    assert 'data-standings-url="/races/2025/1/standings"' in html
    assert "<td>3:27.652</td>" in html
    assert "<td>+0.348</td>" in html
    assert 'id="lap-band"' in html
    assert '<g clip-path="url(#drawn)">' in html
    teammate = "linear-gradient(90deg, #ff8000 0 33%, #000 33% 67%, #ff8000 67%)"
    assert f'<span class="swatch" style="background: {teammate}"></span> <b>PIA</b>' in html
    assert '<span class="swatch" style="background: #ff8000"></span> <b>NOR</b>' in html
    assert '<span class="pit">In Pit</span>' in html
    assert ">Finish</text>" in html


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
