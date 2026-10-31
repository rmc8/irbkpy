from __future__ import annotations

from typing import Literal

from ..models.financials import IndicatorsResponse
from .base import AsyncService, SyncService, build_query_params

PeriodType = Literal["annual", "quarterly", "semiannual"]


class IndicatorsService(SyncService):
    """財務指標・経営指標ドメインの同期サービスクラス

    ROE、ROA、自己資本比率、売上高営業利益率などの主要経営指標を取得します。
    """

    def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
        period: PeriodType = "annual",
    ) -> IndicatorsResponse:
        """指定した銘柄またはEDINETコードの経営指標を取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        期間種別（period）には通期（annual）、四半期（quarterly）、半期（semiannual）を指定可能です。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
            period=period,
        )
        data = self._client._get("/indicators", params=params)
        return IndicatorsResponse.model_validate(data)


class AsyncIndicatorsService(AsyncService):
    """財務指標・経営指標ドメインの非同期サービスクラス

    非同期通信によって主要経営指標を取得します。
    """

    async def get(
        self,
        code: str | None = None,
        security_code: str | None = None,
        edinet_code: str | None = None,
        period: PeriodType = "annual",
    ) -> IndicatorsResponse:
        """指定した銘柄またはEDINETコードの経営指標を非同期で取得します。

        銘柄コード（codeまたはsecurity_code）またはEDINETコード（edinet_code）のいずれかを指定します。
        期間種別（period）には通期（annual）、四半期（quarterly）、半期（semiannual）を指定可能です。
        """
        params = build_query_params(
            security_code=code or security_code,
            edinet_code=edinet_code,
            period=period,
        )
        data = await self._client._get("/indicators", params=params)
        return IndicatorsResponse.model_validate(data)
