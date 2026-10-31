from __future__ import annotations

from ..models.shareholders import ShareholdersResponse
from .base import AsyncService, SyncService, build_query_params


class ShareholdersService(SyncService):
    """大株主情報ドメインの同期サービスクラス

    有価証券報告書等に記載された主要大株主の持株数や持株比率を取得します。
    """

    def list(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
    ) -> ShareholdersResponse:
        """指定した企業の大株主一覧を取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        大株主の名称、保有株式数、持株比率、前期比率を返します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = self._client._get("/shareholders", params=params)
        return ShareholdersResponse.model_validate(data)


class AsyncShareholdersService(AsyncService):
    """大株主情報ドメインの非同期サービスクラス

    非同期通信によって主要大株主の持株数や持株比率を取得します。
    """

    async def list(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
    ) -> ShareholdersResponse:
        """指定した企業の大株主一覧を非同期で取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = await self._client._get("/shareholders", params=params)
        return ShareholdersResponse.model_validate(data)
