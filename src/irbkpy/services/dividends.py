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
        銘柄コードが渡された場合は、自動的に銘柄情報からEDINETコードを解決して問い合わせます。
        """
        sec_code = code or security_code
        resolved_edinet = self._resolve_edinet_code(edinet_code=edinet_code, security_code=sec_code)

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
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
        銘柄コードが渡された場合は、非同期で銘柄情報からEDINETコードを自動解決します。
        """
        sec_code = code or security_code
        resolved_edinet = await self._resolve_edinet_code(
            edinet_code=edinet_code, security_code=sec_code
        )

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
        )
        data = await self._client._get("/dividends", params=params)
        return DividendsResponse.model_validate(data)
