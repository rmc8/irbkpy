# 変更履歴（Changelog）

このプロジェクトにおける重要な変更はすべてこのファイルに記録されます。

フォーマットは[Keep a Changelog](https://keepachangelog.com/ja/1.0.0/)に準拠し、
バージョニングには[セマンティックバージョニング（Semantic Versioning）](https://semver.org/lang/ja/)を採用しています。

## [0.1.2] - 2026-10-31

### 修正および改善

- セグメント情報APIにおけるEDINETコード自動解決の補正
  - `client.segments.list("7203")`のように位置引数で証券コードが指定された場合でも、EDINETコードを自動解決して正常に取得できるよう引数処理を改善しました。
- スクリーニングソート条件の自動正規化
  - `sort_by`に`per:desc`等の方向識別子が付与された場合に自動で末尾を除去し、APIが要求する項目名単体（降順）へ正規化して400エラーを防ぐようにしました。
- 改ページ走査（iter_all等）における安全最小件数の導入
  - `limit`に極小値（4以下等）が指定された際にAPIがカーソルを`***`でマスクして早期終了する問題を防ぐため、内部フェッチ件数に安全最小値（50件）を適用しました。

## [0.1.1] - 2026-10-31

### 修正および改善（Fixed & Improved）

- 配当・セグメント・大株主APIにおけるEDINETコードの自動解決
  - 証券コード（4桁数字等）を指定して`irbk dividends 9020`や`client.dividends.list("9020")`、`segments`、`shareholders`を呼び出した際、銘柄情報からEDINETコード（Eコード）を自動照会して補完する仕組みを実装しました。
- 投資指標テーブルにおけるPBR等の欠損値フォールバック表示
  - `irbk valuations`のテーブル出力において、報告値PBRが欠損している場合に調整後PBR（`pbr_adjusted`）を自動適用し、`-`表示となる問題を解消しました。
- スクリーニング条件式の自動正規化パーサーの導入
  - `roe>=10,per<=15`などの一般的な比較演算子形式で入力された条件式を、API仕様のコロン形式（`roe:gte:10,per:lte:15`）へ自動変換する機能を追加しました。
- カーソル終端処理の強化
  - APIから返却される`next_cursor`が文字列`***`となる場合に終端と判定し、不正カーソルエラーや無限ループを防ぐ安全処理を追加しました。
- 短時間バースト制限（HTTP 429）に対する自動リトライ機能の導入
  - クライアント初期化時に`max_retries`および`retry_backoff`を設定可能とし、429受信時に指数バックオフ待機を行って自動再試行する機構を同期・非同期クライアントへ追加しました。
- CLI実行時の既定ローカルキャッシュ有効化
  - コマンドラインツール`irbk`の実行時に既定でローカルキャッシュを有効化し、APIリクエスト枠の不要な消費を防止するように改善しました（`--no-cache`オプションで無効化可能）。
- 市場区分の日本語入力対応
  - `securities list -m`において「プライム」「スタンダード」「グロース」などの日本語入力からAPI英字識別子（Prime, Standard, Growth）への自動変換に対応しました。
- 対象Pythonバージョンの緩和
  - パッケージの対応Python環境を`>=3.10`へ拡張し、Python 3.10以降の幅広い環境で利用可能としました。
- 市場区分・期間・ランキング指標のEnumおよびリテラル型定義の追加
  - `Market`、`Period`、`SegmentPeriod`、`RankingMetric`の文字列Enum（StrEnum）および対応するLiteral型を導入し、ライブラリ呼び出し時のIDE自動補完や型安全性、CLIでの選択肢表示を向上させました。

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
