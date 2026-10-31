from __future__ import annotations

import json

import httpx
import pytest
from typer.testing import CliRunner

from irbkpy import AsyncIRBankClient, IRBankClient, NotFoundError, RateLimitError
from irbkpy.cli.main import app
from irbkpy.models import SecurityDetail, UsageResponse

runner = CliRunner()


def test_client_init_requires_key():
    with pytest.raises(ValueError, match="IRBank APIのキーが見つかりません"):
        IRBankClient(api_key="")


def test_client_init_with_key():
    client = IRBankClient(api_key="irbk_key_dummy_key_for_testing_12345678901234567890")
    assert client.api_key.startswith("irbk_key_")
    client.close()


def test_client_usage_get():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/usage"
        assert request.headers["authorization"] == "Bearer test_key"
        return httpx.Response(
            200,
            json={
                "limit": 200,
                "used": 12,
                "remaining": 188,
                "resets_at": "2026-07-29T00:00:00+09:00",
            },
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    res = client.usage.get()
    assert isinstance(res, UsageResponse)
    assert res.limit == 200
    assert res.remaining == 188


def test_client_securities_get():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/securities/7203"
        return httpx.Response(
            200,
            json={
                "code": "7203",
                "name": "トヨタ自動車",
                "market": "Prime",
                "industry": "輸送用機器",
                "edinet_code": "E02144",
                "issued_shares": 16314987460,
            },
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    res = client.securities.get("7203")
    assert isinstance(res, SecurityDetail)
    assert res.code == "7203"
    assert res.name == "トヨタ自動車"
    assert res.issued_shares == 16314987460


def test_client_error_handling_404():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={"error": {"code": "not_found", "message": "Security not found"}},
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    with pytest.raises(NotFoundError) as exc_info:
        client.securities.get("9999")
    assert exc_info.value.status_code == 404
    assert exc_info.value.code == "not_found"


def test_client_error_handling_429():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={"error": {"code": "rate_limited", "message": "Daily limit exceeded"}},
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    with pytest.raises(RateLimitError):
        client.usage.get()


@pytest.mark.anyio
async def test_async_client_usage():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/usage"
        return httpx.Response(
            200,
            json={"limit": 200, "used": 5, "remaining": 195},
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport)
    async with AsyncIRBankClient(api_key="test_key", http_client=http_client) as client:
        res = await client.usage.get()
        assert res.used == 5
        assert res.remaining == 195


def test_cli_usage(monkeypatch):
    def mock_get(self):
        return UsageResponse(
            limit=200, used=10, remaining=190, resets_at="2026-07-29T00:00:00+09:00"
        )

    monkeypatch.setattr("irbkpy.services.usage.UsageService.get", mock_get)

    result = runner.invoke(app, ["usage", "--api-key", "test_key"])
    assert result.exit_code == 0
    assert "残り回数" in result.output
    assert "190" in result.output


def test_cli_usage_json(monkeypatch):
    def mock_get(self):
        return UsageResponse(
            limit=200, used=10, remaining=190, resets_at="2026-07-29T00:00:00+09:00"
        )

    monkeypatch.setattr("irbkpy.services.usage.UsageService.get", mock_get)

    result = runner.invoke(app, ["usage", "--api-key", "test_key", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["limit"] == 200
    assert data["remaining"] == 190
