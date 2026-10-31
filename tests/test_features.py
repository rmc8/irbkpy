from __future__ import annotations

import respx

from irbkpy import IRBankClient, PriceRecord, SecurityPricesResponse
from irbkpy.cache import IRBankCache


def test_dataframe_import_error_handling():
    res = SecurityPricesResponse(
        code="7203",
        prices=[PriceRecord(date="2026-01-01", close=2500.0)],
    )

    import pandas as pd
    import polars as pl

    df_pd = res.to_pandas()
    assert isinstance(df_pd, pd.DataFrame)
    assert len(df_pd) == 1
    assert "close" in df_pd.columns

    df_pl = res.to_polars()
    assert isinstance(df_pl, pl.DataFrame)
    assert len(df_pl) == 1
    assert "close" in df_pl.columns


def test_cache_storage(tmp_path):
    db_file = tmp_path / "test_cache.db"
    cache = IRBankCache(db_path=db_file, default_ttl=60)

    key = cache.build_key("https://api.irbank.net/v1/securities/7203", {"limit": 10})
    assert cache.get(key) is None

    data = {"code": "7203", "name": "トヨタ自動車"}
    cache.set(key, data, status_code=200)

    cached_data = cache.get(key)
    assert cached_data == data

    # Clear cache
    cache.clear()
    assert cache.get(key) is None


@respx.mock
def test_client_caching_behavior(tmp_path):
    db_file = tmp_path / "client_cache.db"
    client = IRBankClient(
        api_key="test_key",
        enable_cache=True,
        cache_path=str(db_file),
    )

    # Mock endpoint
    route = respx.get("https://api.irbank.net/v1/securities/7203").respond(
        200,
        json={"code": "7203", "name": "トヨタ自動車"},
    )

    # First call: hits HTTP
    sec1 = client.securities.get("7203")
    assert sec1.code == "7203"
    assert route.call_count == 1

    # Second call: served from cache, HTTP is not hit!
    sec2 = client.securities.get("7203")
    assert sec2.code == "7203"
    assert route.call_count == 1

    # Clear cache and call again: hits HTTP
    client.clear_cache()
    sec3 = client.securities.get("7203")
    assert sec3.code == "7203"
    assert route.call_count == 2


def test_cli_version_option():
    from typer.testing import CliRunner

    from irbkpy import __version__
    from irbkpy.cli.main import app

    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert f"irbkpy {__version__}" in result.stdout

    result_short = runner.invoke(app, ["-v"])
    assert result_short.exit_code == 0
    assert f"irbkpy {__version__}" in result_short.stdout


def test_cli_screening_asc_value_error_formatting():
    from typer.testing import CliRunner

    from irbkpy.cli.main import app

    runner = CliRunner()
    result = runner.invoke(
        app,
        ["screening", "run", "per<=15", "--sort-by", "per:asc", "-k", "dummy_key"],
    )
    assert result.exit_code == 2
    assert "エラー:" in result.stderr
    assert "降順（desc）ソートのみ対応しています" in result.stderr
    assert "Traceback" not in result.stderr
