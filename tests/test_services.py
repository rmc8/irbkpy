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
