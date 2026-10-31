from __future__ import annotations

from ..models.valuations import ValuationsResponse
from .base import AsyncService, SyncService, build_query_params


class ValuationsService(SyncService):
    """投資指標・バリュエーションドメインの同期サービスクラス

    株価収益率（PER）、株価純資産倍率（PBR）、配当利回り、時価総額などのバリュエーション指標を取得します。
    """

    def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
    ) -> ValuationsResponse:
        """指定した企業のバリュエーション指標データを取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        予想PER、実績PBR、PSR、PCFRなどの推移履歴を返します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = self._client._get("/valuations", params=params)
        return ValuationsResponse.model_validate(data)


class AsyncValuationsService(AsyncService):
    """投資指標・バリュエーションドメインの非同期サービスクラス

    非同期通信によって企業の投資指標・バリュエーションデータを取得します。
    """

    async def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
    ) -> ValuationsResponse:
        """指定した企業のバリュエーション指標データを非同期で取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = await self._client._get("/valuations", params=params)
        return ValuationsResponse.model_validate(data)
