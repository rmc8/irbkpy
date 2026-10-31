from __future__ import annotations

from collections.abc import AsyncIterator, Iterator

from ..models.disclosures import DisclosuresListResponse
from ..models.persons import OfficersResponse
from ..models.securities import (
    PriceRecord,
    SecuritiesListResponse,
    SecurityDetail,
    SecurityMarginDailyResponse,
    SecurityPricesResponse,
    SecuritySummary,
    SecurityWeeklyMarginResponse,
)
from ..types import Industry, IndustryType, Market, MarketType
from .base import AsyncService, SyncService, build_query_params, normalize_market_name


class SecuritiesService(SyncService):
    """有価証券ドメインの同期サービスクラス

    銘柄一覧の取得や株価、日歩・逆日歩、信用取引残高、役員一覧、適時開示一覧の取得を提供します。
    """

    def list(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        industry: Industry | IndustryType | str | None = None,
        market: Market | MarketType | str | None = None,
    ) -> SecuritiesListResponse:
        """銘柄一覧を取得します。

        取得件数上限（limit、最大500件）、改ページカーソル（cursor）、業種名（industry）、市場区分（market、Prime/Standard/Growthまたは日本語指定）による絞り込みが可能です。
        """
        norm_market = normalize_market_name(market)
        params = build_query_params(
            limit=limit, cursor=cursor, industry=industry, market=norm_market
        )
        data = self._client._get("/securities", params=params)
        return SecuritiesListResponse.model_validate(data)

    def iter_all(
        self,
        limit: int = 100,
        industry: Industry | IndustryType | str | None = None,
        market: Market | MarketType | str | None = None,
    ) -> Iterator[SecuritySummary]:
        """全銘柄をカーソルページネーションしながら順次走査します。

        1回あたりの取得件数上限（limit、APIカーソルの安定性のため最小50件を推奨）、業種（industry）、市場（market）を指定できます。
        全ページの銘柄データをジェネレーターとして順番に返します。
        """
        # API仕様上、limitが小さすぎるとカーソルが***でマスクされてページングが止まるため安全最小値を適用
        fetch_limit = max(limit, 50) if limit > 0 else 100
        cursor: str | None = None
        while True:
            resp = self.list(limit=fetch_limit, cursor=cursor, industry=industry, market=market)
            yield from resp.securities
            if not resp.next_cursor or resp.next_cursor == "***":
                break
            cursor = resp.next_cursor

    def get(self, code: str) -> SecurityDetail:
        """指定した銘柄コードの詳細情報を取得します。

        企業名、業種、上場市場、決算月、設立年月日などの属性情報を返します。
        """
        data = self._client._get(f"/securities/{code}")
        return SecurityDetail.model_validate(data)

    def get_prices(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SecurityPricesResponse:
        """指定した銘柄コードの株価四本値および出来高を取得します。

        取得開始日（from_date、YYYY-MM-DD形式）、取得終了日（to_date）、件数上限（limit、最大500件）、改ページカーソル（cursor）を指定できます。
        """
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            cursor=cursor,
        )
        data = self._client._get(f"/securities/{code}/prices", params=params)
        return SecurityPricesResponse.model_validate(data)

    def iter_prices(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 100,
    ) -> Iterator[PriceRecord]:
        """指定した銘柄の株価履歴を改ページしながら順次走査します。

        期間（from_dateからto_date）内の全株価レコードをジェネレーターとして順番に返します。
        """
        fetch_limit = max(limit, 50) if limit > 0 else 100
        cursor: str | None = None
        while True:
            resp = self.get_prices(
                code=code,
                from_date=from_date,
                to_date=to_date,
                limit=fetch_limit,
                cursor=cursor,
            )
            yield from resp.prices
            if not resp.next_cursor or resp.next_cursor == "***":
                break
            cursor = resp.next_cursor

    def get_jsf_margin_daily(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> SecurityMarginDailyResponse:
        """日証金の日次信用取引速報および貸借倍率、日歩・逆日歩データを取得します。

        銘柄コード（code）を指定し、必要に応じて期間（from_date、to_date）や件数（limit）を絞り込めます。
        """
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        data = self._client._get(f"/securities/{code}/jsf-margin-daily", params=params)
        return SecurityMarginDailyResponse.model_validate(data)

    def get_weekly_margin_balance(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> SecurityWeeklyMarginResponse:
        """取引所発表の週次信用取引残高データを取得します。

        信用買残、信用売残、貸借倍率の推移履歴を返します。
        """
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        data = self._client._get(f"/securities/{code}/weekly-margin-balance", params=params)
        return SecurityWeeklyMarginResponse.model_validate(data)

    def list_officers(self, code: str) -> OfficersResponse:
        """指定した銘柄の役員一覧を取得します。

        役員名、役職、社外役員区分、現任状況などを返します。
        """
        data = self._client._get(f"/securities/{code}/officers")
        return OfficersResponse.model_validate(data)

    def list_disclosures(
        self,
        code: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> DisclosuresListResponse:
        """指定した銘柄の適時開示・法定開示書類の一覧を取得します。

        有価証券報告書、決算短信、適時開示などの表題やPDFリンクを返します（最大100件）。
        """
        params = build_query_params(limit=limit, cursor=cursor)
        data = self._client._get(f"/securities/{code}/disclosures", params=params)
        return DisclosuresListResponse.model_validate(data)


class AsyncSecuritiesService(AsyncService):
    """有価証券ドメインの非同期サービスクラス

    非同期通信によって銘柄一覧や株価、日証金残高、役員、適時開示を取得します。
    """

    async def list(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        industry: Industry | IndustryType | str | None = None,
        market: Market | MarketType | str | None = None,
    ) -> SecuritiesListResponse:
        """銘柄一覧を非同期で取得します。"""
        norm_market = normalize_market_name(market)
        params = build_query_params(
            limit=limit, cursor=cursor, industry=industry, market=norm_market
        )
        data = await self._client._get("/securities", params=params)
        return SecuritiesListResponse.model_validate(data)

    async def iter_all(
        self,
        limit: int = 100,
        industry: Industry | IndustryType | str | None = None,
        market: Market | MarketType | str | None = None,
    ) -> AsyncIterator[SecuritySummary]:
        """全銘柄を非同期でカーソルページネーションしながら順次走査します。"""
        fetch_limit = max(limit, 50) if limit > 0 else 100
        cursor: str | None = None
        while True:
            resp = await self.list(
                limit=fetch_limit, cursor=cursor, industry=industry, market=market
            )
            for item in resp.securities:
                yield item
            if not resp.next_cursor or resp.next_cursor == "***":
                break
            cursor = resp.next_cursor

    async def get(self, code: str) -> SecurityDetail:
        """指定した銘柄コードの詳細情報を非同期で取得します。"""
        data = await self._client._get(f"/securities/{code}")
        return SecurityDetail.model_validate(data)

    async def get_prices(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> SecurityPricesResponse:
        """指定した銘柄コードの株価四本値を非同期で取得します。"""
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            cursor=cursor,
        )
        data = await self._client._get(f"/securities/{code}/prices", params=params)
        return SecurityPricesResponse.model_validate(data)

    async def iter_prices(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int = 100,
    ) -> AsyncIterator[PriceRecord]:
        """指定した銘柄の株価履歴を非同期で走査します。"""
        fetch_limit = max(limit, 50) if limit > 0 else 100
        cursor: str | None = None
        while True:
            resp = await self.get_prices(
                code=code,
                from_date=from_date,
                to_date=to_date,
                limit=fetch_limit,
                cursor=cursor,
            )
            for price in resp.prices:
                yield price
            if not resp.next_cursor or resp.next_cursor == "***":
                break
            cursor = resp.next_cursor

    async def get_jsf_margin_daily(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> SecurityMarginDailyResponse:
        """日証金の日次信用取引速報および貸借倍率、日歩・逆日歩データを非同期で取得します。"""
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        data = await self._client._get(f"/securities/{code}/jsf-margin-daily", params=params)
        return SecurityMarginDailyResponse.model_validate(data)

    async def get_weekly_margin_balance(
        self,
        code: str,
        from_date: str | None = None,
        to_date: str | None = None,
        limit: int | None = None,
    ) -> SecurityWeeklyMarginResponse:
        """取引所発表の週次信用取引残高データを非同期で取得します。"""
        params = build_query_params(
            {"from_date": "from", "to_date": "to"},
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        data = await self._client._get(f"/securities/{code}/weekly-margin-balance", params=params)
        return SecurityWeeklyMarginResponse.model_validate(data)

    async def list_officers(self, code: str) -> OfficersResponse:
        """指定した銘柄の役員一覧を非同期で取得します。"""
        data = await self._client._get(f"/securities/{code}/officers")
        return OfficersResponse.model_validate(data)

    async def list_disclosures(
        self,
        code: str,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> DisclosuresListResponse:
        """指定した銘柄の適時開示・法定開示書類の一覧を非同期で取得します。"""
        params = build_query_params(limit=limit, cursor=cursor)
        data = await self._client._get(f"/securities/{code}/disclosures", params=params)
        return DisclosuresListResponse.model_validate(data)
