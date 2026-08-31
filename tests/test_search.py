import asyncio

import httpx
from spiderweb_mcp.tools import search


class _Response:
    def __init__(self, status_code: int = 200, results: list[dict] | None = None) -> None:
        self.status_code = status_code
        self._results = results or []

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "backend failed", request=httpx.Request("GET", "http://test"), response=httpx.Response(self.status_code)
            )

    def json(self) -> dict:
        return {"results": self._results}


class _Client:
    def __init__(self, response: _Response | Exception, calls: list[dict]) -> None:
        self.response = response
        self.calls = calls

    async def __aenter__(self) -> "_Client":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def get(self, url: str, params: dict) -> _Response:
        self.calls.append(params)
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


class _MCP:
    def tool(self):
        def decorator(function):
            self.web_search = function
            return function

        return decorator


def _web_search(monkeypatch, clients: list[_Client]):
    monkeypatch.setattr(search.httpx, "AsyncClient", lambda timeout: clients.pop(0))
    mcp = _MCP()
    search.register_search_tools(mcp)
    return mcp.web_search


def test_web_search_probes_before_query(monkeypatch) -> None:
    calls: list[dict] = []
    web_search = _web_search(
        monkeypatch,
        [_Client(_Response(), calls), _Client(_Response(results=[{"title": "T", "url": "U", "content": "C"}]), calls)],
    )

    result = asyncio.run(web_search("python", max_results=1))

    assert result == "### T\nURL: U\nC"
    assert calls == [
        {"q": "_health", "format": "json"},
        {"q": "python", "format": "json"},
    ]


def test_web_search_returns_actionable_message_when_probe_cannot_connect(monkeypatch) -> None:
    calls: list[dict] = []
    web_search = _web_search(monkeypatch, [_Client(httpx.ConnectError("refused"), calls)])

    result = asyncio.run(web_search("python"))

    assert "Local SearXNG instance is unreachable" in result
    assert "docker compose -f docker/docker-compose.yml up -d searxng" in result
    assert calls == [{"q": "_health", "format": "json"}]


def test_web_search_skips_query_when_probe_is_unhealthy(monkeypatch) -> None:
    calls: list[dict] = []
    web_search = _web_search(monkeypatch, [_Client(_Response(status_code=503), calls)])

    result = asyncio.run(web_search("python"))

    assert result == "SearXNG returned status 503. Is the container running?"
    assert calls == [{"q": "_health", "format": "json"}]


def test_web_search_no_results(monkeypatch) -> None:
    """When query yields zero results, return informative message."""
    calls: list[dict] = []
    web_search = _web_search(
        monkeypatch,
        [_Client(_Response(), calls), _Client(_Response(results=[]), calls)],
    )

    result = asyncio.run(web_search("super_obscure_query_12345"))

    assert "No results found for query: super_obscure_query_12345" in result
