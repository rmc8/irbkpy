from __future__ import annotations

from ..models.industries import IndustriesResponse
from .base import AsyncService, SyncService


class IndustriesService(SyncService):
    """業種分類ドメインの同期サービスクラス

    証券コード協議会（SICC）が定める33業種および17業種の分類一覧を取得します。
    """

    def list(self) -> IndustriesResponse:
        """業種分類一覧を取得します。

        東証33業種および17業種の業種コードと名称の一覧を返します。
        """
        data = self._client._get("/industries")
        return IndustriesResponse.model_validate(data)


class AsyncIndustriesService(AsyncService):
    """業種分類ドメインの非同期サービスクラス

    非同期通信によって業種分類一覧を取得します。
    """

    async def list(self) -> IndustriesResponse:
        """業種分類一覧を非同期で取得します。"""
        data = await self._client._get("/industries")
        return IndustriesResponse.model_validate(data)
