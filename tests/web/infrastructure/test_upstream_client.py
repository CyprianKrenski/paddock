import httpx2

from web.infrastructure.http import upstream_client


def test_upstream_client_opens_a_fresh_connection_per_request() -> None:
    client = upstream_client("http://catalogue:8000", timeout=30.0)

    pool = client._transport._pool  # type: ignore[attr-defined]
    assert pool._max_keepalive_connections == 0
    assert str(client.base_url) == "http://catalogue:8000"
    assert client.timeout == httpx2.Timeout(30.0)
