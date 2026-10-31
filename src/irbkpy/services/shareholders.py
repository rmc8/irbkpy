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
        銘柄コードが渡された場合は、自動的にEDINETコードを解決して問い合わせます。
        """
        sec_code = code or security_code
        resolved_edinet = self._resolve_edinet_code(edinet_code=edinet_code, security_code=sec_code)

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
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
        銘柄コードが渡された場合は、非同期でEDINETコードを自動解決します。
        """
        sec_code = code or security_code
        resolved_edinet = await self._resolve_edinet_code(
            edinet_code=edinet_code, security_code=sec_code
        )

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
        )
        data = await self._client._get("/shareholders", params=params)
        return ShareholdersResponse.model_validate(data)
