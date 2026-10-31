from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class IRBankError(Exception):
    """IRBankクライアントが送出する例外の基底クラスです。"""


class IRBankAPIError(IRBankError):
    """IRBank APIからエラー応答を受信した際に送出される例外クラスです。"""

    def __init__(
        self,
        status_code: int,
        code: str | None = None,
        message: str | None = None,
        details: list[dict[str, Any]] | None = None,
        raw_response: httpx.Response | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message or f"HTTP {status_code}"
        self.details = details or []
        self.raw_response = raw_response
        super().__init__(f"[{status_code}] {self.code}: {self.message}")


class BadRequestError(IRBankAPIError):
    """不正な引数や無効なカーソルなど、HTTP 400を受信した際に送出される例外です。"""


class AuthenticationError(IRBankAPIError):
    """APIキーの未設定や無効なキーなど、HTTP 401を受信した際に送出される例外です。"""


class ForbiddenError(IRBankAPIError):
    """権限不足や規約未同意など、HTTP 403を受信した際に送出される例外です。"""


class NotFoundError(IRBankAPIError):
    """指定された銘柄や書類が存在しないなど、HTTP 404を受信した際に送出される例外です。"""


class RateLimitError(IRBankAPIError):
    """レート制限や日次リクエスト上限に到達し、HTTP 429を受信した際に送出される例外です。"""


class ServerError(IRBankAPIError):
    """サーバー側の一時的障害など、HTTP 5xxを受信した際に送出される例外です。"""


def raise_for_status(
    status_code: int,
    data: dict[str, Any] | None = None,
    raw_response: httpx.Response | None = None,
) -> None:
    """HTTPステータスコードを評価し、エラー時に適切な例外クラスを送出します。

    APIから返却されたJSONペイロードのerrorオブジェクトを解析し、機械可読コードや
    詳細メッセージを抽出して対応する例外インスタンスを生成します。
    """
    if status_code < 400:
        return

    error_data = (data or {}).get("error", {}) if isinstance(data, dict) else {}
    code = error_data.get("code")
    message = error_data.get("message")
    details = error_data.get("details")

    kwargs = {
        "status_code": status_code,
        "code": code,
        "message": message,
        "details": details,
        "raw_response": raw_response,
    }

    if status_code == 400:
        raise BadRequestError(**kwargs)
    elif status_code == 401:
        raise AuthenticationError(**kwargs)
    elif status_code == 403:
        raise ForbiddenError(**kwargs)
    elif status_code == 404:
        raise NotFoundError(**kwargs)
    elif status_code == 429:
        raise RateLimitError(**kwargs)
    elif status_code >= 500:
        raise ServerError(**kwargs)
    else:
        raise IRBankAPIError(**kwargs)
