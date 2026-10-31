from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models.disclosures import (
    DisclosureDetailResponse,
    DisclosureMeta,
    DisclosureSectionResponse,
    DisclosuresListResponse,
)
from .base import AsyncService, SyncService, build_query_params


class DisclosuresService(SyncService):
    """開示書類ドメインの同期サービスクラス

    有価証券報告書や決算短信、適時開示などの書類一覧、書類詳細、章別テキスト本文を取得します。
    """

    def list(
        self,
        code: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> DisclosuresListResponse:
        """指定した銘柄コードの開示書類一覧を取得します。

        銘柄コード（code）を指定し、必要に応じて件数上限（limit）や改ページカーソル（cursor）を指定できます。
        """
        params = build_query_params(limit=limit, cursor=cursor)
        data = self._client._get(f"/securities/{code}/disclosures", params=params)
        return DisclosuresListResponse.model_validate(data)

    def iter_all(
        self,
        code: str,
        limit: int = 100,
    ) -> Iterator[DisclosureMeta]:
        """指定した銘柄の全開示書類をカーソルページネーションしながら順次走査します。

        全ページの書類メタデータをジェネレーターとして順番に返します。
        """
        cursor: str | None = None
        while True:
            resp = self.list(code=code, limit=limit, cursor=cursor)
            yield from resp.disclosures
            if not resp.next_cursor:
                break
            cursor = resp.next_cursor

    def get(self, doc_id: str) -> DisclosureDetailResponse:
        """指定した書類ID（doc_id）の詳細メタデータおよびセクション一覧を取得します。

        抽出されたXBRLファクトや取得可能なセクション一覧を返します。
        """
        data = self._client._get(f"/disclosures/{doc_id}")
        return DisclosureDetailResponse.model_validate(data)

    def get_section(self, doc_id: str, section: str) -> DisclosureSectionResponse:
        """指定した書類IDおよびセクション名の本文テキストを取得します。

        事業等のリスク、経営方針、経営成績等の概況など、有価証券報告書の特定セクションのテキスト本文を返します。
        """
        data = self._client._get(f"/disclosures/{doc_id}/sections/{section}")
        return DisclosureSectionResponse.model_validate(data)


class AsyncDisclosuresService(AsyncService):
    """開示書類ドメインの非同期サービスクラス

    非同期通信によって開示書類一覧、書類詳細、章別テキスト本文を取得します。
    """

    async def list(
        self,
        code: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> DisclosuresListResponse:
        """指定した銘柄コードの開示書類一覧を非同期で取得します。"""
        params = build_query_params(limit=limit, cursor=cursor)
        data = await self._client._get(f"/securities/{code}/disclosures", params=params)
        return DisclosuresListResponse.model_validate(data)

    async def iter_all(
        self,
        code: str,
        limit: int = 100,
    ) -> AsyncIterator[DisclosureMeta]:
        """指定した銘柄の全開示書類を非同期で走査します。"""
        cursor: str | None = None
        while True:
            resp = await self.list(code=code, limit=limit, cursor=cursor)
            for item in resp.disclosures:
                yield item
            if not resp.next_cursor:
                break
            cursor = resp.next_cursor

    async def get(self, doc_id: str) -> DisclosureDetailResponse:
        """指定した書類IDの詳細情報を非同期で取得します。"""
        data = await self._client._get(f"/disclosures/{doc_id}")
        return DisclosureDetailResponse.model_validate(data)

    async def get_section(self, doc_id: str, section: str) -> DisclosureSectionResponse:
        """指定した書類IDおよびセクション名のテキスト本文を非同期で取得します。"""
        data = await self._client._get(f"/disclosures/{doc_id}/sections/{section}")
        return DisclosureSectionResponse.model_validate(data)
