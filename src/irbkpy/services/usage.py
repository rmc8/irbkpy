from __future__ import annotations

from ..models.usage import UsageResponse
from .base import AsyncService, SyncService


class UsageService(SyncService):
    """API利用状況ドメインの同期サービスクラス

    契約プランに応じた当日のAPIリクエスト上限および残り利用回数を取得します。
    """

    def get(self) -> UsageResponse:
        """当日のAPI利用状況ステータスを取得します。

        利用回数上限、使用済み回数、残り回数、リセット予定時刻を返します。
        キャッシュを迂回して常に最新の状況を取得します。
        """
        data = self._client._get("/usage")
        return UsageResponse.model_validate(data)


class AsyncUsageService(AsyncService):
    """API利用状況ドメインの非同期サービスクラス

    非同期通信によって当日のAPI利用状況ステータスを取得します。
    """

    async def get(self) -> UsageResponse:
        """当日のAPI利用状況ステータスを非同期で取得します。"""
        data = await self._client._get("/usage")
        return UsageResponse.model_validate(data)
