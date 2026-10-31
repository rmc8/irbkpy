from __future__ import annotations

from ..models.peers import PeersResponse
from .base import AsyncService, SyncService, build_query_params


class PeersService(SyncService):
    """競合企業・類似銘柄ドメインの同期サービスクラス

    指定企業と同業または事業内容の類似した企業群の指標データを取得します。
    """

    def list(
        self,
        code: str | None = None,
        security_code: str | None = None,
        limit: int = 8,
    ) -> PeersResponse:
        """指定した銘柄の類似企業一覧および比較指標を取得します。

        銘柄コード（codeまたはsecurity_code）と取得件数（limit、初期値8）を指定します。
        売上高、営業利益、PER、時価総額などの比較データを返します。
        """
        params = build_query_params(
            security_code=code or security_code,
            limit=limit,
        )
        data = self._client._get("/peers", params=params)
        return PeersResponse.model_validate(data)


class AsyncPeersService(AsyncService):
    """競合企業・類似銘柄ドメインの非同期サービスクラス

    非同期通信によって類似企業一覧および比較指標を取得します。
    """

    async def list(
        self,
        code: str | None = None,
        security_code: str | None = None,
        limit: int = 8,
    ) -> PeersResponse:
        """指定した銘柄の類似企業一覧および比較指標を非同期で取得します。

        銘柄コード（codeまたはsecurity_code）と取得件数（limit）を指定します。
        """
        params = build_query_params(
            security_code=code or security_code,
            limit=limit,
        )
        data = await self._client._get("/peers", params=params)
        return PeersResponse.model_validate(data)
