from __future__ import annotations

import httpx
from typer.testing import CliRunner

from irbkpy import (
    FinancialsResponse,
    IndicatorsResponse,
    IRBankClient,
    PeersResponse,
    ScreeningResponse,
    SecurityDetail,
)
from irbkpy.cli.main import app

runner = CliRunner()


def test_financials_and_indicators():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v1/financials" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "edinet_code": "E02144",
                    "fields": [{"key": "sales", "label": "売上高", "unit": "jpy"}],
                    "periods": [
                        {
                            "fiscal_year": "2025/03",
                            "sales": 45000000000000,
                            "operating_income": 5000000000000,
                        }
                    ],
                },
            )
        elif "/v1/indicators" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "edinet_code": "E02144",
                    "fields": [{"key": "roe", "label": "ROE", "unit": "ratio"}],
                    "periods": [{"fiscal_year": "2025/03", "roe": 14.5, "equity_ratio": 42.1}],
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    fin = client.financials.get(code="7203")
    assert isinstance(fin, FinancialsResponse)
    assert len(fin.periods) == 1
    assert fin.periods[0]["sales"] == 45000000000000

    ind = client.indicators.get(code="7203")
    assert isinstance(ind, IndicatorsResponse)
    assert ind.periods[0]["roe"] == 14.5


def test_screening_and_peers():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v1/screening" in request.url.path:
            assert request.url.params["filters"] == "roe:gte:10"
            return httpx.Response(
                200,
                json={
                    "total_count": 1,
                    "securities": [
                        {
                            "security_code": "7203",
                            "name": "トヨタ自動車",
                            "metrics": [{"field": "roe", "value": 14.5, "as_of": "2025-03"}],
                        }
                    ],
                },
            )
        elif "/v1/peers" in request.url.path:
            return httpx.Response(
                200,
                json={
                    "security_code": "7203",
                    "peers": [
                        {
                            "security_code": "7267",
                            "name": "本田技研工業",
                            "industry": "輸送用機器",
                            "segments": ["自動車"],
                        }
                    ],
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    scr = client.screening.screen(filters=["roe:gte:10"])
    assert isinstance(scr, ScreeningResponse)
    assert scr.total_count == 1
    assert scr.securities[0].security_code == "7203"

    peers = client.peers.list(code="7203")
    assert isinstance(peers, PeersResponse)
    assert peers.peers[0].security_code == "7267"


def test_cli_securities_commands(monkeypatch):
    def mock_get(self, code):
        return SecurityDetail(code=code, name="トヨタ自動車", market="Prime", industry="輸送用機器")

    monkeypatch.setattr("irbkpy.services.securities.SecuritiesService.get", mock_get)

    result = runner.invoke(app, ["securities", "get", "7203", "--api-key", "test_key"])
    assert result.exit_code == 0
    assert "トヨタ自動車" in result.output
    assert "Prime" in result.output


def test_edinet_auto_resolution():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/v1/securities/9020" in request.url.path:
            return httpx.Response(
                200,
                json={"code": "9020", "name": "東日本旅客鉄道", "edinet_code": "E04147"},
            )
        elif "/v1/dividends" in request.url.path:
            assert request.url.params.get("edinet_code") == "E04147"
            return httpx.Response(
                200,
                json={
                    "edinet_code": "E04147",
                    "records": [{"fiscal_year": 2026, "annual_dps": 74}],
                },
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    # 証券コード9020を指定しても内部でEDINETコードE04147が自動解決される
    divs = client.dividends.list(code="9020")
    assert divs.edinet_code == "E04147"
    assert divs.records[0].annual_dps == 74


def test_screening_filter_normalization():
    def handler(request: httpx.Request) -> httpx.Response:
        # roe>=10,per<=15がroe:gte:10,per:lte:15に変換されているか検証
        filters = request.url.params.get("filters")
        assert "roe:gte:10" in filters
        assert "per:lte:15" in filters
        return httpx.Response(200, json={"total_count": 0, "securities": []})

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    res = client.screening.screen(filters=["roe>=10", "per<=15"])
    assert res.total_count == 0


def test_cursor_asterisk_termination():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            200,
            json={
                "securities": [{"code": "7203", "name": "トヨタ"}],
                "next_cursor": "***",  # APIが終端に***を返すケース
            },
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(api_key="test_key", http_client=http_client)

    items = list(client.securities.iter_all(limit=10))
    assert len(items) == 1
    assert call_count == 1  # ***で無限ループにならず1回で終了する


def test_rate_limit_retry():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(429, json={"error": {"code": "rate_limited"}})
        return httpx.Response(200, json={"limit": 200, "used": 1, "remaining": 199})

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = IRBankClient(
        api_key="test_key",
        http_client=http_client,
        max_retries=2,
        retry_backoff=0.01,  # テスト用に短い待機時間
    )

    usage = client.usage.get()
    assert usage.remaining == 199
    assert call_count == 2
