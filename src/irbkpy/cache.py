from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any


class IRBankCache:
    """SQLiteをバックエンドとするIRBank API応答キャッシュマネージャです。

    同一条件のHTTPリクエストに対してキャッシュされたデータを返却し、
    日次リクエスト枠の消費を抑えつつ高速に応答します。
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        default_ttl: int = 86400,
    ) -> None:
        """キャッシュマネージャを初期化します。

        データベースファイルのパスが省略された場合は、ユーザーのホームディレクトリ配下
        （~/.cache/irbkpy/http_cache.db）に自動作成します。既定の有効期間は24時間（86400秒）です。
        """
        self.default_ttl = default_ttl
        if db_path is None:
            cache_dir = Path.home() / ".cache" / "irbkpy"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = str(cache_dir / "http_cache.db")
        else:
            self.db_path = str(db_path)

        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """データベース接続を生成して返します。"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """キャッシュ格納用のテーブルが存在しない場合に作成します。"""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS response_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
                """
            )
            conn.commit()

    @staticmethod
    def build_key(url: str, params: dict[str, Any] | None = None) -> str:
        """URLとクエリパラメータから一意なキャッシュ識別キーを生成します。

        パラメータの順序に依存しないよう、キー名でソートして正規化したクエリ文字列を構築します。
        """
        param_str = ""
        if params:
            sorted_items = sorted((k, str(v)) for k, v in params.items() if v is not None)
            param_str = "&".join(f"{k}={v}" for k, v in sorted_items)
        return f"{url}?{param_str}" if param_str else url

    def get(self, key: str) -> dict[str, Any] | None:
        """指定されたキーに一致する有効なキャッシュデータを取得します。

        有効期限が切れているレコードはデータベースから自動削除し、Noneを返します。
        """
        now = time.time()
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT data, expires_at FROM response_cache WHERE cache_key = ?",
                (key,),
            ).fetchone()
            if row is None:
                return None
            if row["expires_at"] < now:
                conn.execute("DELETE FROM response_cache WHERE cache_key = ?", (key,))
                conn.commit()
                return None
            try:
                parsed: dict[str, Any] = json.loads(row["data"])
                return parsed
            except Exception:
                return None

    def set(
        self,
        key: str,
        data: dict[str, Any],
        status_code: int = 200,
        ttl: int | None = None,
    ) -> None:
        """レスポンスデータをJSON形式でシリアライズしてキャッシュへ保存します。

        HTTP 200以外のステータスコードや空データはキャッシュしません。
        """
        if status_code != 200 or data is None:
            return
        now = time.time()
        expires = now + (ttl if ttl is not None else self.default_ttl)
        try:
            serialized = json.dumps(data, ensure_ascii=False)
        except Exception:
            return

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO response_cache (cache_key, data, status_code, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (key, serialized, status_code, now, expires),
            )
            conn.commit()

    def clear(self) -> None:
        """保存されているすべてのキャッシュレコードを削除します。"""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM response_cache")
            conn.commit()
