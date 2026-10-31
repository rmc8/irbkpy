from __future__ import annotations

from ..models.organizations import Organization
from .base import AsyncService, SyncService


class OrganizationsService(SyncService):
    """法人組織情報ドメインの同期サービスクラス

    EDINETコードに基づく提出者情報や法人基本情報を取得します。
    """

    def get(self, edinet_code: str) -> Organization:
        """指定したEDINETコードの法人組織情報を取得します。

        法人名、英語名称、所在地、法人番号、提出者区分などを返します。
        """
        data = self._client._get(f"/organizations/{edinet_code}")
        return Organization.model_validate(data)


class AsyncOrganizationsService(AsyncService):
    """法人組織情報ドメインの非同期サービスクラス

    非同期通信によって法人組織情報を取得します。
    """

    async def get(self, edinet_code: str) -> Organization:
        """指定したEDINETコードの法人組織情報を非同期で取得します。"""
        data = await self._client._get(f"/organizations/{edinet_code}")
        return Organization.model_validate(data)
