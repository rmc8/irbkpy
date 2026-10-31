from __future__ import annotations

from typing import Literal

from ..models.segments import SegmentsResponse
from .base import AsyncService, SyncService, build_query_params

SegmentPeriod = Literal["annual", "quarter"]


class SegmentsService(SyncService):
    """事業セグメント情報ドメインの同期サービスクラス

    企業の事業セグメント別売上高、営業利益、資産などの内訳データを取得します。
    """

    def list(
        self,
        edinet_code: str | None = None,
        code: str | None = None,
        security_code: str | None = None,
        fiscal_year: int | None = None,
        period: SegmentPeriod = "annual",
    ) -> SegmentsResponse:
        """指定した企業の事業セグメント別業績データを取得します。

        EDINETコード（edinet_code）または銘柄コード（code、security_code）を指定します。
        銘柄コードが渡された場合は、自動的にEDINETコードを解決して問い合わせます。
        """
        sec_code = code or security_code
        resolved_edinet = self._resolve_edinet_code(edinet_code=edinet_code, security_code=sec_code)

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
            fiscal_year=fiscal_year,
            period=period,
        )
        data = self._client._get("/segments", params=params)
        return SegmentsResponse.model_validate(data)


class AsyncSegmentsService(AsyncService):
    """事業セグメント情報ドメインの非同期サービスクラス

    非同期通信によって企業の事業セグメント別業績データを取得します。
    """

    async def list(
        self,
        edinet_code: str | None = None,
        code: str | None = None,
        security_code: str | None = None,
        fiscal_year: int | None = None,
        period: SegmentPeriod = "annual",
    ) -> SegmentsResponse:
        """指定した企業の事業セグメント別業績データを非同期で取得します。

        EDINETコード（edinet_code）または銘柄コード（code、security_code）を指定します。
        銘柄コードが渡された場合は、非同期でEDINETコードを自動解決します。
        """
        sec_code = code or security_code
        resolved_edinet = await self._resolve_edinet_code(
            edinet_code=edinet_code, security_code=sec_code
        )

        params = build_query_params(
            security_code=sec_code,
            edinet_code=resolved_edinet or edinet_code,
            fiscal_year=fiscal_year,
            period=period,
        )
        data = await self._client._get("/segments", params=params)
        return SegmentsResponse.model_validate(data)
