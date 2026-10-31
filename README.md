# irbkpy

[![PyPI version](https://img.shields.io/pypi/v/irbkpy.svg?color=blue)](https://pypi.org/project/irbkpy/)
[![Python versions](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/irbkpy/)
[![CI status](https://img.shields.io/github/actions/workflow/status/rmc8/irbkpy/ci.yml?branch=main&label=CI)](https://github.com/rmc8/irbkpy/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg)](https://docs.pydantic.dev/)

IRBank API（REST）を操作するためのPythonクライアントライブラリおよびCLIツールです。httpxによる高速な同期・非同期通信、Pydantic v2による厳格な型安全性を備え、コマンドラインからも即座に企業データへアクセスできます。

## 主な特徴

- 全26エンドポイントのレスポンスをPydantic v2モデルで構造化しており、IDEの自動補完や静的型チェックに対応します。
- 市場区分（`Market`）、東証33業種（`Industry`）、期間種別（`Period`）、ランキング指標（`RankingMetric`）などの文字列Enum（StrEnum）とLiteral型を完備し、タイプセーフな開発を支援します。
- `IRBankClient`（同期）と`AsyncIRBankClient`（非同期）の両方を提供し、単体スクリプトからFastAPIなどのWebアプリケーションまで柔軟に組み込めます。
- 配当やセグメント、大株主APIにおいて、証券コード（4桁）が指定された場合にEDINETコードを自動照会して透過的に補完します。
- 短時間の連続リクエストによるレート制限（HTTP 429）に対し、自動で指数バックオフ待機を行って再試行します。
- `to_pandas()`や`to_polars()`の呼び出しにより、株価や財務時系列データを1行でDataFrameへ変換できます。
- SQLiteを用いたローカルキャッシュ機構を備え、同一条件の再照会ではAPIとの通信を行わず、日次リクエスト枠を節約します。
- `iter_all()`や`iter_prices()`などのジェネレータ関数により、カーソル指定を気にせず全件を順次取得できます。
- コマンドラインツール`irbk`を同梱しており、ターミナルから財務諸表や株価、ランキングを素早く照会できます。表形式の表示に加え、`--json`出力にも対応します。
- APIキーは引数による直接指定のほか、環境変数（`IRBK_API_KEY`または`IRBANK_API_KEY`）や`.env`ファイルから自動で読み込まれます。

## インストール

```bash
# 基本インストール
pip install irbkpy

# Pandas連携を含める場合
pip install "irbkpy[pandas]"

# Polars連携を含める場合
pip install "irbkpy[polars]"

# すべての連携機能を含める場合
pip install "irbkpy[all]"
```

ローカル開発環境の構築手順（uvを使用する場合）

```bash
uv sync --all-extras
```

## 認証設定

APIキーは[IRBANK Connect](https://app.irbank.net/mcp-api)にて発行できます。
発行されたキーを環境変数に設定してください。

```bash
export IRBK_API_KEY="irbk_key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

カレントディレクトリに`.env`ファイルを配置して設定することも可能です。

```env
IRBK_API_KEY="irbk_key_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
```

## Pythonライブラリとしての利用

### 同期クライアント（IRBankClient）

```python
from irbkpy import Industry, IRBankClient, Market, Period, RankingMetric

# APIキーは環境変数IRBK_API_KEYまたは.envから自動解決されます
with IRBankClient() as client:
    # 1. 銘柄詳細の取得
    security = client.securities.get("7203")
    print(f"{security.name}（{security.code}）- {security.market}")

    # 2. 日次株価の取得
    prices = client.securities.get_prices("7203", limit=5)
    for p in prices.prices:
        print(f"{p.date} 終値{p.close}円（調整後{p.adj_close}円）")

    # 3. 財務時系列の取得（Period Enumによる指定）
    financials = client.financials.get(code="7203", period=Period.ANNUAL)
    for period in financials.periods:
        print(f"{period.get('fiscal_year')} 売上高{period.get('sales'):,}円")

    # 4. 年次配当実績の取得（証券コードからEDINETコードを自動解決）
    dividends = client.dividends.list("7203")
    for d in dividends.history[:3]:
        print(f"{d.fiscal_year} 1株配当{d.annual_dps_adjusted or d.annual_dps}円")

    # 5. 条件スクリーニング（比較演算子による直感的な条件指定）
    results = client.screening.screen(
        filters=["roe>=10", "per<=15"],
        sort_by="roe:desc",
        limit=10,
    )
    for s in results.securities:
        print(s.security_code, s.name)

    # 6. 市場ランキングの取得（RankingMetric Enumによる指定）
    ranking = client.rankings.get(RankingMetric.GAINERS, limit=5)
    for item in ranking.items:
        print(f"{item.get('rank')}位 {item.get('name')}（{item.get('security_code')}）")
```

### PandasおよびPolarsへの変換

株価時系列や財務諸表、スクリーニング結果などを直接DataFrameへ変換できます。

```python
from irbkpy import IRBankClient

with IRBankClient() as client:
    # 日次株価をpandas DataFrameへ変換
    prices = client.securities.get_prices("7203", limit=60)
    df_prices = prices.to_pandas()
    print(df_prices.head())

    # 財務指標をpolars DataFrameへ変換
    indicators = client.indicators.get(code="7203")
    df_ind = indicators.to_polars()
    print(df_ind)
```

### ローカルキャッシュ機能（リクエスト上限の節約）

`enable_cache=True`を指定するとSQLiteベースのキャッシュが有効化されます。同一日かつ同一条件のリクエストは通信を発生させず、ローカルから即座にデータを取得します。

```python
from irbkpy import IRBankClient

# キャッシュを有効化（有効期間は秒単位で指定、既定値は24時間）
with IRBankClient(enable_cache=True, cache_ttl=86400) as client:
    # 初回呼び出しではサーバーと通信してキャッシュへ保存
    sec = client.securities.get("7203")

    # 2回目以降はキャッシュから即時取得（APIの日次リクエスト枠を消費しません）
    sec_cached = client.securities.get("7203")

    # 手動でキャッシュを破棄する場合
    client.clear_cache()
```

### 自動ページネーション

```python
from irbkpy import Industry, IRBankClient, Market

with IRBankClient() as client:
    # 東証プライム市場・輸送用機器の全銘柄を逐次取得
    for sec in client.securities.iter_all(
        market=Market.PRIME, industry=Industry.TRANSPORTATION_EQUIPMENT
    ):
        print(sec.code, sec.name)
```

### 非同期クライアント（AsyncIRBankClient）

```python
import asyncio
from irbkpy import AsyncIRBankClient


async def main():
    async with AsyncIRBankClient() as client:
        # 株価と指標を並行して取得
        price_task = client.securities.get_prices("7203", limit=1)
        indicator_task = client.indicators.get(code="7203")

        price_res, indicator_res = await asyncio.gather(price_task, indicator_task)
        print("最新株価", price_res.prices[0].close)
        print("最新指標", indicator_res.periods[0])


asyncio.run(main())
```

### 例外処理

```python
from irbkpy import IRBankClient
from irbkpy.exceptions import AuthenticationError, NotFoundError, RateLimitError

with IRBankClient() as client:
    try:
        client.securities.get("9999")
    except NotFoundError as e:
        print(f"指定された銘柄が存在しません（コード{e.code}、内容{e.message}）")
    except RateLimitError:
        print("APIの利用上限またはレート制限に達しました。")
    except AuthenticationError:
        print("APIキーが無効、または未設定です。")
```

## CLIツールの利用方法

コマンドラインツール`irbk`が利用できます。

```bash
# ヘルプ一覧の表示
irbk --help

# 本日の残りリクエスト数の確認
irbk usage

# 銘柄一覧の取得（市場区分「プライム」や業種で絞り込み）
irbk securities list --market Prime --industry="輸送用機器" --limit 20

# 銘柄基本情報の取得
irbk securities get 7203

# 日次株価の取得
irbk securities prices 7203 --limit 10

# 財務諸表（損益計算書・貸借対照表等）の取得
irbk financials 7203 --period annual

# 計算済み財務指標（ROE、ROA、自己資本比率等）の取得
irbk indicators 7203

# 年次バリュエーション（PER、PBR、配当利回り等）の取得
irbk valuations 7203

# 年次配当実績の取得（証券コードで照会可能）
irbk dividends 7203

# 競合企業一覧の取得
irbk peers 7203

# 複数条件による銘柄スクリーニング（一般的な比較演算子形式に対応）
irbk screening run "roe>=15,per<=10" --sort-by "per:desc"

# 指標別ランキングの取得（値上がり率、値下がり率、出来高）
irbk rankings gainers --limit 10

# 開示書類一覧の取得
irbk disclosures 7203 --limit 10

# キャッシュを無視して最新データを取得する場合
irbk securities get 7203 --no-cache
```

### JSON出力（他ツールとの連携）

すべてのコマンドで`--json`オプションを指定可能です。整形されたJSONが出力されるため、`jq`コマンド等と組み合わせたパイプライン処理が容易に行えます。

```bash
# 発行済株式数のみを抽出
irbk securities get 7203 --json | jq .issued_shares
```

## 提供エンドポイント一覧

| カテゴリ | エンドポイント | ライブラリAPI | CLIコマンド |
| :--- | :--- | :--- | :--- |
| securities | `GET /securities` | `client.securities.list()`, `iter_all()` | `irbk securities list` |
| | `GET /securities/{code}` | `client.securities.get()` | `irbk securities get` |
| | `GET /securities/{code}/prices` | `client.securities.get_prices()`, `iter_prices()` | `irbk securities prices` |
| | `GET /securities/{code}/jsf-margin-daily` | `client.securities.get_jsf_margin_daily()` | - |
| | `GET /securities/{code}/weekly-margin-balance` | `client.securities.get_weekly_margin_balance()` | - |
| organizations | `GET /organizations/{edinet_code}` | `client.organizations.get()` | - |
| industries | `GET /industries` | `client.industries.list()` | - |
| financials | `GET /financials` | `client.financials.get()` | `irbk financials` |
| indicators | `GET /indicators` | `client.indicators.get()` | `irbk indicators` |
| segments | `GET /segments` | `client.segments.list()` | - |
| dividends | `GET /dividends` | `client.dividends.list()` | `irbk dividends` |
| valuations | `GET /valuations` | `client.valuations.get()` | `irbk valuations` |
| peers | `GET /peers` | `client.peers.list()` | `irbk peers` |
| shareholders | `GET /shareholders` | `client.shareholders.list()` | - |
| persons | `GET /persons/{id}` | `client.persons.get()` | - |
| | `GET /persons/{id}/appointments` | `client.persons.get_appointments()` | - |
| | `GET /persons/{id}/compensation-history` | `client.persons.get_compensation_history()` | - |
| | `GET /persons/{id}/holdings` | `client.persons.get_holdings()` | - |
| | `GET /securities/{code}/officers` | `client.persons.list_officers()` | - |
| disclosures | `GET /securities/{code}/disclosures` | `client.disclosures.list()`, `iter_all()` | `irbk disclosures` |
| | `GET /disclosures/{doc_id}` | `client.disclosures.get()` | - |
| | `GET /disclosures/{doc_id}/sections/{section}` | `client.disclosures.get_section()` | - |
| screening | `GET /screening` | `client.screening.screen()`, `iter_screen()` | `irbk screening run` |
| | `GET /screening/fields` | `client.screening.list_fields()` | `irbk screening fields` |
| rankings | `GET /rankings/{metric}` | `client.rankings.get()` | `irbk rankings` |
| usage | `GET /usage` | `client.usage.get()` | `irbk usage` |

## テストの実行

```bash
uv run pytest
```

## 継続的インテグレーション（CI）とPyPI自動デプロイ

本リポジトリにはGitHub Actionsワークフローを完備しています。

- `ci.yml`
  `main`ブランチへのプッシュおよびプルリクエスト作成時に、`ty check`（型検査）、`ruff check`（静的解析）、`ruff format --check`（コード書式検証）、`pytest`（単体テスト）を自動実行します。
- `release.yml`
  PyPIのTrusted Publishing（OIDC）に準拠した自動デプロイワークフローです。GitHub Releasesでリリースを公開するか、`v0.1.0`形式のGitタグをプッシュすることで自動ビルドされ、PyPIへ公開されます。

### PyPI Trusted Publishingの初期設定手順

1. [PyPIアカウント設定画面](https://pypi.org/manage/account/publishing/)を開きます。
2. 「Add a publisher」を選択し、以下の各項目を設定します。
   - PyPI Project Name欄に`irbkpy`と入力
   - Owner欄に自身のGitHubアカウント名（または組織名）を入力
   - Repository name欄に本リポジトリ名を入力
   - Workflow name欄に`release.yml`と入力
   - Environment name欄に`pypi`と入力
3. 登録完了後は、APIトークンやパスワードをGitHub Secretsへ登録することなく、GitHub Actionsから安全にPyPIへ公開できます。
