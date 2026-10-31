from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ..client import IRBankClient
from ..exceptions import IRBankAPIError
from ..models.base import IRBankBaseModel
from ..types import MarketType, PeriodType, RankingMetric

app = typer.Typer(
    name="irbk",
    help="IRBank APIコマンドラインツール。日本の企業・財務データへアクセスします。",
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)

securities_app = typer.Typer(
    name="securities", help="銘柄情報、株価、信用取引データのコマンド群です。"
)
app.add_typer(securities_app)

screening_app = typer.Typer(name="screening", help="銘柄スクリーニングのコマンド群です。")
app.add_typer(screening_app)


def get_client(api_key: str | None = None, no_cache: bool = False) -> IRBankClient:
    """IRBankClientのインスタンスを生成して返します。

    APIキーが明示的に渡されない場合は環境変数や.envファイルから自動解決します。
    CLI実行時は既定でローカルキャッシュを有効化し、APIリクエスト枠の消費を抑制します。
    """
    try:
        return IRBankClient(api_key=api_key, enable_cache=not no_cache)
    except ValueError as e:
        err_console.print(f"[bold red]エラー:[/bold red] {e}")
        raise typer.Exit(code=1)


def output_result(
    data: IRBankBaseModel | dict[str, Any] | list[Any] | str, as_json: bool = False
) -> None:
    """コマンド実行結果を端末へ出力します。

    as_jsonが真の場合はRichのprint_json機能を用いて整形されたJSONを標準出力へ出力します。
    """
    if as_json:
        if isinstance(data, IRBankBaseModel):
            console.print_json(data.model_dump_json())
        else:
            console.print_json(json.dumps(data, ensure_ascii=False, default=str))
    else:
        console.print(data)


# ----------------------------------------------------------------------
# API利用状況（Usage）
# ----------------------------------------------------------------------
@app.command("usage")
def usage(
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """当日のAPI利用可能残数を確認します。"""
    client = get_client(api_key, no_cache=True)
    try:
        res = client.usage.get()
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title="IRBank API利用状況（本日・日本標準時）")
        table.add_column("上限回数", justify="right", style="cyan")
        table.add_column("使用済み", justify="right", style="magenta")
        table.add_column("残り回数", justify="right", style="green")
        table.add_column("制限リセット時刻", style="yellow")
        table.add_row(str(res.limit), str(res.used), str(res.remaining), str(res.resets_at or "-"))
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# 銘柄（Securities）
# ----------------------------------------------------------------------
@securities_app.command("list")
def securities_list(
    limit: int = typer.Option(50, "--limit", "-l", help="取得件数の上限（最大500件）。"),
    market: MarketType | None = typer.Option(
        None,
        "--market",
        "-m",
        help="市場区分フィルター（Prime, Standard, Growthまたは日本語指定）。",
    ),
    industry: str | None = typer.Option(
        None, "--industry", "-i", help="業種名フィルター（水産・農林業、輸送用機器など）。"
    ),
    cursor: str | None = typer.Option(None, "--cursor", help="改ページ用のカーソル。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """上場銘柄の一覧を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.securities.list(limit=limit, market=market, industry=industry, cursor=cursor)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"上場銘柄一覧（{len(res.securities)}件）")
        table.add_column("銘柄コード", style="cyan", no_wrap=True)
        table.add_column("企業名", style="bold")
        table.add_column("市場区分", style="green")
        table.add_column("業種", style="yellow")

        for s in res.securities:
            table.add_row(s.code, s.name, s.market or "-", s.industry or "-")
        console.print(table)
        if res.next_cursor and res.next_cursor != "***":
            console.print(f"[dim]次ページカーソル: {res.next_cursor}[/dim]")
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


@securities_app.command("get")
def securities_get(
    code: str = typer.Argument(..., help="銘柄コード（例: 7203）。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定銘柄の詳細情報を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.securities.get(code)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"銘柄詳細: {res.name}（{res.code}）")
        table.add_column("項目名", style="cyan")
        table.add_column("値", style="bold")

        table.add_row("銘柄コード", res.code)
        table.add_row("企業名", res.name)
        table.add_row("市場区分", res.market or "-")
        table.add_row("業種", res.industry or "-")
        table.add_row("EDINETコード", res.edinet_code or "-")
        table.add_row("上場ステータス", res.listing_status or "-")
        table.add_row("上場年月", res.listing_month or "-")
        table.add_row("決算期末月", str(res.fiscal_year_end_month or "-"))
        table.add_row("発行済株式数", f"{res.issued_shares:,}" if res.issued_shares else "-")
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


@securities_app.command("prices")
def securities_prices(
    code: str = typer.Argument(..., help="銘柄コード（例: 7203）。"),
    from_date: str | None = typer.Option(None, "--from", help="取得開始日（YYYY-MM-DD）。"),
    to_date: str | None = typer.Option(None, "--to", help="取得終了日（YYYY-MM-DD）。"),
    limit: int = typer.Option(20, "--limit", "-l", help="取得件数の上限（最大500件）。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定銘柄の日次株価四本値を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.securities.get_prices(code, from_date=from_date, to_date=to_date, limit=limit)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"日次株価推移: {code}（{len(res.prices)}件）")
        table.add_column("日付", style="cyan")
        table.add_column("初値", justify="right")
        table.add_column("高値", justify="right")
        table.add_column("安値", justify="right")
        table.add_column("終値", justify="right", style="bold")
        table.add_column("調整後終値", justify="right", style="green")
        table.add_column("出来高", justify="right")

        for p in res.prices:
            table.add_row(
                p.date,
                f"{p.open:,.1f}" if p.open is not None else "-",
                f"{p.high:,.1f}" if p.high is not None else "-",
                f"{p.low:,.1f}" if p.low is not None else "-",
                f"{p.close:,.1f}" if p.close is not None else "-",
                f"{p.adj_close:,.1f}" if p.adj_close is not None else "-",
                f"{p.volume:,.0f}" if p.volume is not None else "-",
            )
        console.print(table)
        if res.next_cursor and res.next_cursor != "***":
            console.print(f"[dim]次ページカーソル: {res.next_cursor}[/dim]")
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# 財務・経営指標（Financials & Indicators）
# ----------------------------------------------------------------------
@app.command("financials")
def financials_cmd(
    code: str = typer.Argument(..., help="銘柄コードまたはEDINETコード。"),
    period: PeriodType = typer.Option(
        "annual", "--period", "-p", help="期間種別（annual、quarterly、semiannual）。"
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """企業の財務諸表時系列データを取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        is_edinet = code.startswith(("E", "G")) and len(code) == 6
        res = client.financials.get(
            edinet_code=code if is_edinet else None,
            code=None if is_edinet else code,
            period=period,
        )
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"財務時系列推移（{code}・{period}）")
        table.add_column("決算期", style="cyan")
        table.add_column("売上高（円）", justify="right")
        table.add_column("営業利益（円）", justify="right")
        table.add_column("当期純利益（円）", justify="right")
        table.add_column("総資産（円）", justify="right")
        table.add_column("純資産（円）", justify="right")

        for p in res.periods:
            sales = p.get("sales") or p.get("revenue")
            op_inc = p.get("operating_income")
            net_inc = p.get("net_income")
            assets = p.get("total_assets")
            net_assets = p.get("net_assets")
            table.add_row(
                str(p.get("fiscal_year", "-")),
                f"{sales:,.0f}" if isinstance(sales, (int, float)) else "-",
                f"{op_inc:,.0f}" if isinstance(op_inc, (int, float)) else "-",
                f"{net_inc:,.0f}" if isinstance(net_inc, (int, float)) else "-",
                f"{assets:,.0f}" if isinstance(assets, (int, float)) else "-",
                f"{net_assets:,.0f}" if isinstance(net_assets, (int, float)) else "-",
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("indicators")
def indicators_cmd(
    code: str = typer.Argument(..., help="銘柄コードまたはEDINETコード。"),
    period: PeriodType = typer.Option(
        "annual", "--period", "-p", help="期間種別（※現在サーバー仕様により通期10期を返却）。"
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """企業の主要経営指標・財務比率の時系列推移を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        is_edinet = code.startswith(("E", "G")) and len(code) == 6
        res = client.indicators.get(
            edinet_code=code if is_edinet else None,
            code=None if is_edinet else code,
            period=period,
        )
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"経営指標推移（{code}・{period}）")
        table.add_column("決算期", style="cyan")
        table.add_column("ROE（%）", justify="right")
        table.add_column("ROA（%）", justify="right")
        table.add_column("自己資本比率（%）", justify="right")
        table.add_column("営業利益率（%）", justify="right")

        for p in res.periods:
            roe = p.get("roe") or p.get("roe_computed")
            roa = p.get("roa")
            eq_ratio = p.get("equity_ratio")
            op_margin = p.get("operating_margin")
            table.add_row(
                str(p.get("fiscal_year", "-")),
                f"{roe:.2f}" if isinstance(roe, (int, float)) else "-",
                f"{roa:.2f}" if isinstance(roa, (int, float)) else "-",
                f"{eq_ratio:.2f}" if isinstance(eq_ratio, (int, float)) else "-",
                f"{op_margin:.2f}" if isinstance(op_margin, (int, float)) else "-",
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# 投資指標・配当（Valuations & Dividends）
# ----------------------------------------------------------------------
@app.command("valuations")
def valuations_cmd(
    code: str = typer.Argument(..., help="銘柄コード（例: 7203）。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定銘柄の年次投資指標推移（PER、PBRなど）を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.valuations.get(code=code)
        if as_json:
            output_result(res, as_json=True)
            return

        title = f"投資指標推移（{code}）"
        if res.per_5y_avg is not None:
            title += f" [過去5年平均PER: {res.per_5y_avg:.1f}倍]"
        table = Table(title=title)
        table.add_column("年度", style="cyan")
        table.add_column("株価", justify="right")
        table.add_column("PER（倍）", justify="right")
        table.add_column("PBR（倍）", justify="right")
        table.add_column("配当利回り（%）", justify="right")
        table.add_column("時価総額（円）", justify="right")

        for h in res.history:
            # 報告値が欠損している場合は調整後値（adjusted）で補完表示
            price_val = h.stock_price if h.stock_price is not None else h.stock_price_adjusted
            pbr_val = h.pbr if h.pbr is not None else h.pbr_adjusted
            yield_val = (
                h.dividend_yield if h.dividend_yield is not None else h.dividend_yield_adjusted
            )

            table.add_row(
                str(h.fiscal_year or "-"),
                f"{price_val:,.1f}" if price_val is not None else "-",
                f"{h.per:.1f}" if h.per is not None else "-",
                f"{pbr_val:.2f}" if pbr_val is not None else "-",
                f"{yield_val:.2f}" if yield_val is not None else "-",
                f"{h.market_cap:,.0f}" if h.market_cap is not None else "-",
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("dividends")
def dividends_cmd(
    code: str = typer.Argument(
        ..., help="銘柄コードまたはEDINETコード（証券コード指定時は自動解決されます）。"
    ),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """企業の配当履歴および配当指標データを取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        is_edinet = code.startswith(("E", "G")) and len(code) == 6
        res = client.dividends.list(
            edinet_code=code if is_edinet else None,
            code=None if is_edinet else code,
        )
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"配当履歴推移（{code}）")
        table.add_column("決算期", style="cyan")
        table.add_column("1株配当（円）", justify="right")
        table.add_column("調整後1株配当（円）", justify="right")
        table.add_column("配当性向（%）", justify="right")
        table.add_column("DOE（%）", justify="right")
        table.add_column("連続増配年数", justify="right")

        for r in res.records:
            table.add_row(
                str(r.fiscal_year or "-"),
                f"{r.annual_dps:,.1f}" if r.annual_dps is not None else "-",
                f"{r.annual_dps_adjusted:,.1f}" if r.annual_dps_adjusted is not None else "-",
                f"{r.payout_ratio:.1f}" if r.payout_ratio is not None else "-",
                f"{r.doe:.1f}" if r.doe is not None else "-",
                str(r.consecutive_growth_years or "-"),
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# 競合企業（Peers）
# ----------------------------------------------------------------------
@app.command("peers")
def peers_cmd(
    code: str = typer.Argument(..., help="銘柄コード（例: 7203）。"),
    limit: int = typer.Option(8, "--limit", "-l", help="取得件数の上限（最大20件）。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定銘柄の競合企業・類似銘柄一覧を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.peers.list(code=code, limit=limit)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"競合企業比較（{code}）")
        table.add_column("銘柄コード", style="cyan")
        table.add_column("企業名", style="bold")
        table.add_column("業種", style="yellow")
        table.add_column("重複セグメント", style="green")
        table.add_column("選定理由")

        for p in res.peers:
            segs = ", ".join(p.segments) if p.segments else "-"
            table.add_row(
                p.security_code, p.name or "-", p.industry or "-", segs, p.competition_reason or "-"
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# スクリーニング（Screening）
# ----------------------------------------------------------------------
@screening_app.command("run")
def screening_run(
    filters: str = typer.Argument(
        ...,
        help='カンマ区切りの条件式（例: "per:lte:15,roe:gte:10" または "per<=15,roe>=10"）。',
    ),
    sort_by: str | None = typer.Option(
        None, "--sort-by", "-s", help="並び替え基準（例: per:asc, per:desc）。"
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="取得件数の上限。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """複数条件による銘柄スクリーニングを実行します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.screening.screen(filters=filters, sort_by=sort_by, limit=limit)
        if as_json:
            output_result(res, as_json=True)
            return

        title = f"スクリーニング結果（{len(res.securities)}銘柄"
        if res.total_count is not None:
            title += f" / 該当総数: {res.total_count}"
        title += "）"
        table = Table(title=title)
        table.add_column("銘柄コード", style="cyan")
        table.add_column("企業名", style="bold")
        table.add_column("抽出指標値", style="green")

        for s in res.securities:
            metric_strs = []
            for m in s.metrics:
                if hasattr(m, "field"):
                    metric_strs.append(f"{m.field}={m.value}")
                elif isinstance(m, dict):
                    metric_strs.append(f"{m.get('field')}={m.get('value')}")
            table.add_row(
                s.security_code, s.name or "-", ", ".join(metric_strs) if metric_strs else "-"
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


@screening_app.command("fields")
def screening_fields(
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """スクリーニングで利用可能な指標・項目一覧を表示します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.screening.list_fields()
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"利用可能スクリーニング項目（{len(res.fields)}項目）")
        table.add_column("キー名", style="cyan")
        table.add_column("項目表示名", style="bold")
        table.add_column("単位", style="green")
        table.add_column("型区分", style="yellow")
        table.add_column("説明")

        for f in res.fields:
            table.add_row(f.key, f.label or "-", f.unit or "-", f.type or "-", f.note or "-")
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# ランキング（Rankings）
# ----------------------------------------------------------------------
@app.command("rankings")
def rankings_cmd(
    metric: RankingMetric = typer.Argument(..., help="指標キー（gainers, losers, volume）。"),
    target_date: str | None = typer.Option(None, "--date", "-d", help="基準日（YYYY-MM-DD）。"),
    limit: int = typer.Option(20, "--limit", "-l", help="取得件数の上限。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定指標の市場ランキングデータを取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.rankings.get(metric, target_date=target_date, limit=limit)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"市場ランキング: {res.metric}（基準日: {res.target_date or '最新'}）")
        table.add_column("順位", justify="right", style="cyan")
        table.add_column("銘柄コード", style="cyan")
        table.add_column("企業名", style="bold")
        table.add_column("業種", style="yellow")
        table.add_column("終値", justify="right")
        table.add_column("騰落率", justify="right")

        for item in res.items:
            rank = item.get("rank", "-")
            code = item.get("security_code", "-")
            name = item.get("name", "-")
            ind = item.get("industry_name", "-")
            close = item.get("close_price")
            chg = item.get("change_percent")
            table.add_row(
                str(rank),
                str(code),
                str(name),
                str(ind),
                f"{close:,.1f}" if isinstance(close, (int, float)) else "-",
                f"{chg:+.2f}%" if isinstance(chg, (int, float)) else "-",
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


# ----------------------------------------------------------------------
# 適時開示・法定開示（Disclosures）
# ----------------------------------------------------------------------
@app.command("disclosures")
def disclosures_cmd(
    code: str = typer.Argument(..., help="銘柄コード（例: 7203）。"),
    limit: int = typer.Option(20, "--limit", "-l", help="取得件数の上限（最大100件）。"),
    no_cache: bool = typer.Option(False, "--no-cache", help="ローカルキャッシュを無効化します。"),
    api_key: str | None = typer.Option(None, "--api-key", "-k", help="IRBank APIキー。"),
    as_json: bool = typer.Option(False, "--json", help="未加工のJSONを出力します。"),
) -> None:
    """指定銘柄の開示書類一覧を取得します。"""
    client = get_client(api_key, no_cache=no_cache)
    try:
        res = client.disclosures.list(code, limit=limit)
        if as_json:
            output_result(res, as_json=True)
            return

        table = Table(title=f"開示書類一覧: {code}（{len(res.disclosures)}件）")
        table.add_column("書類ID", style="cyan")
        table.add_column("提出日", style="yellow")
        table.add_column("開示元", style="green")
        table.add_column("書類種別")
        table.add_column("表題", style="bold")

        for d in res.disclosures:
            table.add_row(
                d.doc_id,
                d.filing_date or "-",
                d.source or "-",
                d.document_type or "-",
                d.title or "-",
            )
        console.print(table)
    except IRBankAPIError as e:
        err_console.print(f"[bold red]APIエラー:[/bold red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
