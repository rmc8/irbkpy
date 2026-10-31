from __future__ import annotations

from ..models.dividends import DividendsResponse
from .base import AsyncService, SyncService, build_query_params


class DividendsService(SyncService):
    """配当情報ドメインの同期サービスクラス

    1株当たり配当金、配当性向、株主資本配当率（DOE）、配当利回りなどの配当履歴データを取得します。
    """

    def list(
        self,
        edinet_code: str | None = None,
        code: str | None = None,
        security_code: str | None = None,
    ) -> DividendsResponse:
        """指定した企業の配当履歴および配当指標データを取得します。

        EDINETコード（edinet_code）または銘柄コード（code、security_code）を指定します。
        中間配当、期末配当、年間配当の推移履歴を返します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = self._client._get("/dividends", params=params)
        return DividendsResponse.model_validate(data)


class AsyncDividendsService(AsyncService):
    """配当情報ドメインの非同期サービスクラス

    非同期通信によって企業の配当履歴および配当指標データを取得します。
    """

    async def list(
        self,
        edinet_code: str | None = None,
        code: str | None = None,
        security_code: str | None = None,
    ) -> DividendsResponse:
        """指定した企業の配当履歴および配当指標データを非同期で取得します。

        EDINETコード（edinet_code）または銘柄コード（code、security_code）を指定します。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
        )
        data = await self._client._get("/dividends", params=params)
        return DividendsResponse.model_validate(data)
