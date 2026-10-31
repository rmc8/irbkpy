from __future__ import annotations

import os
from pathlib import Path

# IRBank REST APIの基準URL
DEFAULT_BASE_URL = "https://api.irbank.net/v1"

# HTTPリクエストの既定タイムアウト秒数
DEFAULT_TIMEOUT = 30.0


def load_env_file(dotenv_path: Path | str | None = None) -> None:
    """指定されたパスの.envファイルを読み込み、未設定の環境変数を補完します。

    外部ライブラリに依存せず、シンプルな構文解析によりキーと値のペアを抽出して
    os.environへ格納します。すでに環境変数が設定されている場合は上書きしません。
    """
    if dotenv_path is None:
        path = Path.cwd() / ".env"
    else:
        path = Path(dotenv_path)

    if not path.is_file():
        return

    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                # 空行やコメント行、等号を含まない行は読み飛ばす
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, val = stripped.split("=", 1)
                clean_key = key.strip()
                clean_val = val.strip().strip("'\"")
                if clean_key and clean_key not in os.environ:
                    os.environ[clean_key] = clean_val
    except Exception:
        # ファイル読み込みに失敗した場合も処理を継続する
        pass


def resolve_api_key(api_key: str | None = None) -> str:
    """APIキーを解決して返します。

    引数で明示的に指定されたキーを最優先とし、未指定の場合はカレントディレクトリの.envファイル、
    環境変数（IRBK_API_KEYまたはIRBANK_API_KEY）の順序で探索します。キーが見つからない場合は
    ValueErrorを送出します。
    """
    if api_key:
        return api_key

    # カレントディレクトリの.envファイルからの読み込みを試みる
    load_env_file()

    key = os.environ.get("IRBK_API_KEY") or os.environ.get("IRBANK_API_KEY")
    if not key:
        raise ValueError(
            "IRBank APIのキーが見つかりません。引数api_keyを指定するか、"
            "環境変数IRBK_API_KEY（またはIRBANK_API_KEY）を設定してください。"
        )
    return key
