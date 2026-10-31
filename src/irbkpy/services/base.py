from __future__ import annotations

from typing import TYPE_CHECKING, Any

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


class SyncService:
    """同期サービスクラスの基底クラス

    同期HTTPクライアントのインスタンスを保持し、各ドメインごとのAPI呼び出しを仲介します。
    """

    def __init__(self, client: IRBankClient) -> None:
        self._client = client


class AsyncService:
    """非同期サービスクラスの基底クラス

    非同期HTTPクライアントのインスタンスを保持し、各ドメインごとのAPI呼び出しを仲介します。
    """

    def __init__(self, client: AsyncIRBankClient) -> None:
        self._client = client
