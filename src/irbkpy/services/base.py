from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from ..types import Market, MarketType

if TYPE_CHECKING:
    from ..client import AsyncIRBankClient, IRBankClient


def build_query_params(
    mapping: dict[str, str] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """値がNoneでない項目のみを抽出したクエリパラメータ辞書を生成します。

    Pythonの予約語や引数名と異なるクエリキー（例: from_dateからfromへの置換）は
    mapping辞書に定義することで自動変換されます。
    """
    rename_map = mapping or {}
    params: dict[str, Any] = {}
    for key, val in kwargs.items():
        if val is not None:
            query_key = rename_map.get(key, key)
            params[query_key] = val
    return params


def normalize_filter_expression(expr: str) -> str:
    """スクリーニング条件式をAPIが要求するfield:op:value形式へ正規化します。

    ユーザーがroe>=10やper<=15などの比較演算子で入力した場合、
    API仕様であるroe:gte:10やper:lte:15へ自動変換します。
    すでにコロン形式で入力されている場合はそのまま返します。
    """
    trimmed = expr.strip()
    if ":" in trimmed:
        return trimmed

    # 比較演算子の置換規則（長い演算子を先に照合）
    operators = [
        (">=", ":gte:"),
        ("<=", ":lte:"),
        (">", ":gt:"),
        ("<", ":lt:"),
        ("==", ":eq:"),
        ("=", ":eq:"),
    ]
    for op, replacement in operators:
        if op in trimmed:
            parts = trimmed.split(op, 1)
            field = parts[0].strip()
            value = parts[1].strip()
            return f"{field}{replacement}{value}"
    return trimmed


def normalize_market_name(market: Market | MarketType | str | None) -> str | None:
    """日本語の市場区分名やMarket EnumをAPIが要求する英字名称（Prime, Standard, Growth）へ正規化します。"""
    if not market:
        return None
    raw_str = market.value if isinstance(market, Enum) else str(market)
    market_map = {
        "プライム": "Prime",
        "プライム市場": "Prime",
        "prime": "Prime",
        "スタンダード": "Standard",
        "スタンダード市場": "Standard",
        "standard": "Standard",
        "グロース": "Growth",
        "グロース市場": "Growth",
        "growth": "Growth",
    }
    cleaned = raw_str.strip()
    return market_map.get(cleaned, cleaned)


class SyncService:
    """同期サービスクラスの基底クラス

    同期HTTPクライアントのインスタンスを保持し、各ドメインごとのAPI呼び出しを仲介します。
    """

    def __init__(self, client: IRBankClient) -> None:
        self._client = client

    def _resolve_edinet_code(
        self,
        edinet_code: str | None = None,
        security_code: str | None = None,
    ) -> str | None:
        """EDINETコードが未指定で証券コードが渡された場合、銘柄情報から自動解決します。"""
        if edinet_code:
            return edinet_code
        if not security_code:
            return None
        # EまたはGから始まる6桁文字列はすでにEDINETコード
        cleaned = security_code.strip().upper()
        if cleaned.startswith(("E", "G")) and len(cleaned) == 6:
            return cleaned
        # 証券コードから銘柄詳細を取得してEDINETコードを解決
        try:
            detail = self._client.securities.get(cleaned)
            return detail.edinet_code
        except Exception:
            return None


class AsyncService:
    """非同期サービスクラスの基底クラス

    非同期HTTPクライアントのインスタンスを保持し、各ドメインごとのAPI呼び出しを仲介します。
    """

    def __init__(self, client: AsyncIRBankClient) -> None:
        self._client = client

    async def _resolve_edinet_code(
        self,
        edinet_code: str | None = None,
        security_code: str | None = None,
    ) -> str | None:
        """EDINETコードが未指定で証券コードが渡された場合、銘柄情報から非同期で自動解決します。"""
        if edinet_code:
            return edinet_code
        if not security_code:
            return None
        cleaned = security_code.strip().upper()
        if cleaned.startswith(("E", "G")) and len(cleaned) == 6:
            return cleaned
        try:
            detail = await self._client.securities.get(cleaned)
            return detail.edinet_code
        except Exception:
            return None
