import httpx2

from web.entities.errors import NotFound, UpstreamDown


def upstream_client(base_url: str, timeout: float) -> httpx2.Client:
    limits = httpx2.Limits(max_keepalive_connections=0)
    return httpx2.Client(base_url=base_url, timeout=timeout, limits=limits)


def call(http: httpx2.Client, method: str, path: str, timeout: float | None = None) -> object:
    try:
        response = http.request(
            method, path, timeout=httpx2.USE_CLIENT_DEFAULT if timeout is None else timeout
        )
    except httpx2.TransportError as error:
        raise UpstreamDown(f"{http.base_url} unreachable: {error}") from error
    if response.status_code == 404:
        raise NotFound(str(response.json().get("detail", path)))
    if response.status_code >= 400:
        raise UpstreamDown(f"{http.base_url}{path} answered {response.status_code}")
    return response.json()
