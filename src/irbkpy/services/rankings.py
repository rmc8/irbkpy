from __future__ import annotations

from ..models.rankings import RankingResponse
from ..types import RankingMetric, RankingMetricType
from .base import AsyncService, SyncService, build_query_params


class RankingsService(SyncService):
    """市場ランキングドメインの同期サービスクラス

    値上がり率、値下がり率、出来高、売買代金などの市場ランキングデータを取得します。
    """

    def get(
        self,
        metric: RankingMetric | RankingMetricType | str,
        target_date: str | None = None,
        limit: int | None = None,
    ) -> RankingResponse:
        """指定した指標名（metric）の市場ランキングを取得します。

        指標名（metric、例: gainers, losers, volume）、対象日（target_date、YYYY-MM-DD形式）、件数上限（limit）を指定可能です。
        """
        params = build_query_params(target_date=target_date, limit=limit)
        data = self._client._get(f"/rankings/{metric}", params=params)
        return RankingResponse.model_validate(data)


class AsyncRankingsService(AsyncService):
    """市場ランキングドメインの非同期サービスクラス

    非同期通信によって市場ランキングデータを取得します。
    """

    async def get(
        self,
        metric: RankingMetric | RankingMetricType | str,
        target_date: str | None = None,
        limit: int | None = None,
    ) -> RankingResponse:
        """指定した指標名（metric）の市場ランキングを非同期で取得します。"""
        params = build_query_params(target_date=target_date, limit=limit)
        data = await self._client._get(f"/rankings/{metric}", params=params)
        return RankingResponse.model_validate(data)
