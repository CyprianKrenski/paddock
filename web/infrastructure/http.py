import httpx2

from web.entities.errors import NotFound, UpstreamDown


def call(http: httpx2.Client, method: str, path: str) -> object:
    try:
        response = http.request(method, path)
    except httpx2.TransportError as error:
        raise UpstreamDown(f"{http.base_url} unreachable: {error}") from error
    if response.status_code == 404:
        raise NotFound(str(response.json().get("detail", path)))
    if response.status_code >= 400:
        raise UpstreamDown(f"{http.base_url}{path} answered {response.status_code}")
    return response.json()
