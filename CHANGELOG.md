# 変更履歴（Changelog）

このプロジェクトにおける重要な変更はすべてこのファイルに記録されます。

フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.0.0/)に準拠し、
バージョニングには[セマンティックバージョニング（Semantic Versioning）](https://semver.org/lang/ja/)を採用しています。

## [0.1.0] - 2026-10-31

### 追加（Added）

- HTTPXベースのIRBank REST APIクライアント
  - 同期クライアント`IRBankClient`および非同期クライアント`AsyncIRBankClient`の実装
  - コンテキストマネージャ（`with`および`async with`）による確実な接続管理
  - APIキーの自動解決機能（引数指定、環境変数`IRBK_API_KEY`または`IRBANK_API_KEY`、`.env`ファイルからの自動読み込み）

- Pydantic v2による厳格な型安全モデル
  - 全26エンドポイントに対応するレスポンスモデル群（`models/`）
  - APIの将来的な仕様変更や項目追加に対応する`ConfigDict(extra="allow")`構成
  - クレジット情報やエラー要因等の共通メタデータモデル（`Attribution`、`Reason`、`FieldInfo`）

- ドメイン別サービスクラス
  - `securities`（上場銘柄一覧、銘柄詳細、日次株価、日証金貸借残高、週次信用残高の取得）
  - `organizations`（EDINETコード指定による法人基本情報の取得）
  - `industries`（東証17/33業種マスタ一覧の取得）
  - `financials`（財務諸表時系列（PL、BS、キャッシュフロー等）の取得）
  - `indicators`（計算済み財務指標時系列（ROE、ROA、自己資本比率等）の取得）
  - `segments`（セグメント別業績（年度および単独四半期）の取得）
  - `dividends`（年次配当実績および連続増配年数の取得）
  - `valuations`（年次バリュエーション時系列（PER、PBR、配当利回り、時価総額等）の取得）
  - `peers`（有価証券報告書の競合分析に基づく競合企業一覧の取得）
  - `shareholders`（大株主リスト（大量保有報告書ベース）の取得）
  - `persons`（役員一覧、人物プロファイル、就任履歴、報酬履歴、保有株式の取得）
  - `disclosures`（開示書類一覧（EDINET/TDnet）、詳細情報、本文セクションテキストの取得）
  - `screening`（複数条件による銘柄スクリーニングおよび指標カタログの取得）
  - `rankings`（市場横断の指標別ランキングの取得）
  - `usage`（当日の残りリクエスト可能数の取得）

- 自動ページネーション機能
  - カーソル指定によるページ遷移を隠蔽し、全件を順次取得できるジェネレータ関数群（`iter_all()`、`iter_prices()`、`iter_screen()`等）の実装

- データ分析フレームワーク連携（Pandas / Polars）
  - オプション依存関係`irbkpy[pandas]`、`irbkpy[polars]`、`irbkpy[all]`の定義
  - 主要レスポンスモデルへの`.to_pandas()`および`.to_polars()`変換メソッドの実装

- SQLiteによるローカルキャッシュ機能
  - `IRBankClient(enable_cache=True)`によるリクエスト結果のローカル保存
  - 重複リクエスト時の通信抑止による、API日次枠の節約と応答速度の向上
  - 残量確認エンドポイント（`/usage`）に対する自動キャッシュ除外処理

- TyperおよびRichによるCLIツール（irbk）
  - 各種データ照会サブコマンド（`usage`、`securities`、`financials`、`indicators`、`valuations`、`dividends`、`peers`、`screening`、`rankings`、`disclosures`）
  - Richを活用した表形式の整形出力
  - シェルスクリプトや`jq`との連携を可能にする`--json`出力オプション

- 堅牢なエラーハンドリング
  - `IRBankAPIError`を基底としたステータスコード別の例外クラス群（`BadRequestError`、`AuthenticationError`、`ForbiddenError`、`NotFoundError`、`RateLimitError`、`ServerError`）

- 品質管理とCI/CD環境
  - Astral社のtyによる静的型検査（`ty check`）への完全対応
  - Astral社のruffによるコード規約検証および書式統一
  - `pytest`および`respx`による単体テストスイートの整備
  - GitHub Actionsによる自動テストワークフロー（`ci.yml`）
  - PyPI Trusted Publishing（OIDC認証）によるリリース自動化ワークフロー（`release.yml`）
