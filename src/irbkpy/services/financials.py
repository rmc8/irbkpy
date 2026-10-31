from __future__ import annotations

from ..models.financials import FinancialsResponse
from ..types import Period, PeriodType
from .base import AsyncService, SyncService, build_query_params


class FinancialsService(SyncService):
    """財務情報ドメインの同期サービスクラス

    企業の貸借対照表、損益計算書、キャッシュフロー計算書などの財務諸表データを取得します。
    """

    def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
        period: Period | PeriodType | str = "annual",
        as_of: str | None = None,
    ) -> FinancialsResponse:
        """指定した銘柄またはEDINETコードの財務情報を取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        期間種別（period）には通期（annual）、四半期（quarterly）、半期（semiannual）を指定可能です。
        基準日（as_of、YYYY-MM-DD形式）を指定することで、過去時点の財務データに遡及して取得できます。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
            period=period,
            as_of=as_of,
        )
        data = self._client._get("/financials", params=params)
        return FinancialsResponse.model_validate(data)


class AsyncFinancialsService(AsyncService):
    """財務情報ドメインの非同期サービスクラス

    非同期通信によって企業の財務諸表データを取得します。
    """

    async def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
        period: Period | PeriodType | str = "annual",
        as_of: str | None = None,
    ) -> FinancialsResponse:
        """指定した銘柄またはEDINETコードの財務情報を非同期で取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        期間種別（period）には通期（annual）、四半期（quarterly）、半期（semiannual）を指定可能です。
        基準日（as_of）を指定すると、過去時点の財務データに遡及して取得できます。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
            period=period,
            as_of=as_of,
        )
        data = await self._client._get("/financials", params=params)
        return FinancialsResponse.model_validate(data)
