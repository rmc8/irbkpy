from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models.screening import ScreenedSecurity, ScreeningFieldsResponse, ScreeningResponse
from .base import AsyncService, SyncService, build_query_params


class ScreeningService(SyncService):
    """銘柄スクリーニングドメインの同期サービスクラス

    複数の財務指標やバリュエーション条件を組み合わせた銘柄抽出機能を提供します。
    """

    def screen(
        self,
        filters: str | list[str],
        sort_by: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ScreeningResponse:
        """指定したフィルター条件に基づいて銘柄を検索・抽出します。

        フィルター条件（filters、カンマ区切り文字列または文字列リスト、例: ["roe>=10", "per<=15"]）、並び替え指定（sort_by）、件数上限（limit）、改ページカーソル（cursor）を指定できます。
        """
        filter_str = ",".join(filters) if isinstance(filters, (list, tuple)) else filters
        params = build_query_params(
            filters=filter_str,
            sort_by=sort_by,
            limit=limit,
            cursor=cursor,
        )
        data = self._client._get("/screening", params=params)
        return ScreeningResponse.model_validate(data)

    def iter_screen(
        self,
        filters: str | list[str],
        sort_by: str | None = None,
        limit: int = 100,
    ) -> Iterator[ScreenedSecurity]:
        """フィルター条件に合致する全銘柄をカーソルページネーションしながら順次走査します。

        全該当銘柄をジェネレーターとして順番に返します。
        """
        cursor: str | None = None
        while True:
            resp = self.screen(filters=filters, sort_by=sort_by, limit=limit, cursor=cursor)
            yield from resp.securities
            if not resp.next_cursor:
                break
            cursor = resp.next_cursor

    def list_fields(self) -> ScreeningFieldsResponse:
        """スクリーニングで利用可能な指標・項目の一覧を取得します。

        各項目のキー名、表示名、単位、型区分を返します。
        """
        data = self._client._get("/screening/fields")
        return ScreeningFieldsResponse.model_validate(data)


class AsyncScreeningService(AsyncService):
    """銘柄スクリーニングドメインの非同期サービスクラス

    非同期通信によって銘柄の複合条件抽出を行います。
    """

    async def screen(
        self,
        filters: str | list[str],
        sort_by: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ScreeningResponse:
        """指定したフィルター条件に基づいて銘柄を非同期で抽出します。"""
        filter_str = ",".join(filters) if isinstance(filters, (list, tuple)) else filters
        params = build_query_params(
            filters=filter_str,
            sort_by=sort_by,
            limit=limit,
            cursor=cursor,
        )
        data = await self._client._get("/screening", params=params)
        return ScreeningResponse.model_validate(data)

    async def iter_screen(
        self,
        filters: str | list[str],
        sort_by: str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[ScreenedSecurity]:
        """フィルター条件に合致する全銘柄を非同期で順次走査します。"""
        cursor: str | None = None
        while True:
            resp = await self.screen(filters=filters, sort_by=sort_by, limit=limit, cursor=cursor)
            for item in resp.securities:
                yield item
            if not resp.next_cursor:
                break
            cursor = resp.next_cursor

    async def list_fields(self) -> ScreeningFieldsResponse:
        """スクリーニング利用可能項目一覧を非同期で取得します。"""
        data = await self._client._get("/screening/fields")
        return ScreeningFieldsResponse.model_validate(data)
