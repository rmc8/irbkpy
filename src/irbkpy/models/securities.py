from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class SecuritySummary(IRBankBaseModel):
    """上場銘柄の要約情報（証券コード、銘柄名、市場区分、業種）です。"""

    code: str
    name: str
    market: str | None = None
    industry: str | None = None


class SecuritiesListResponse(IRBankBaseModel):
    """上場銘柄一覧API（GET /securities）の応答モデルです。"""

    securities: list[SecuritySummary] = []
    next_cursor: str | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """銘柄一覧をpandasのDataFrameへ変換します。"""
        return records_to_pandas([s.model_dump() for s in self.securities])

    def to_polars(self) -> pl.DataFrame:
        """銘柄一覧をpolarsのDataFrameへ変換します。"""
        return records_to_polars([s.model_dump() for s in self.securities])


class SecurityDetail(IRBankBaseModel):
    """銘柄詳細API（GET /securities/{code}）の応答モデルです。"""

    code: str
    name: str
    market: str | None = None
    industry: str | None = None
    edinet_code: str | None = None
    listing_status: str | None = None
    delisting_date: str | None = None
    listing_month: str | None = None
    fiscal_year_end_month: int | None = None
    issued_shares: int | None = None
    attribution: Attribution | None = None


class PriceRecord(IRBankBaseModel):
    """日次四本値、調整後終値、出来高などの個別株価レコードです。"""

    date: str
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float | None = None
    adj_close: float | None = None
    volume: float | None = None


class SecurityPricesResponse(IRBankBaseModel):
    """銘柄の日次株価API（GET /securities/{code}/prices）の応答モデルです。"""

    code: str | None = None
    fields: list[FieldInfo] = []
    prices: list[PriceRecord] = []
    next_cursor: str | None = None
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """株価時系列レコードをpandasのDataFrameへ変換します。"""
        return records_to_pandas([p.model_dump() for p in self.prices])

    def to_polars(self) -> pl.DataFrame:
        """株価時系列レコードをpolarsのDataFrameへ変換します。"""
        return records_to_polars([p.model_dump() for p in self.prices])


class SecurityMarginDailyResponse(IRBankBaseModel):
    """日証金貸借取引残高・逆日歩APIの応答モデルです。"""

    security_code: str | None = None
    name: str | None = None
    industry_name: str | None = None
    issued_shares_count: int | None = None
    exchange: str | None = None
    period: str | None = None
    fields: list[FieldInfo] = []
    days: list[dict[str, Any]] = []
    reverse: list[dict[str, Any]] = []
    other_exchange_reverse: list[dict[str, Any]] = []
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """日次貸借残高データをpandasのDataFrameへ変換します。"""
        return records_to_pandas(self.days)

    def to_polars(self) -> pl.DataFrame:
        """日次貸借残高データをpolarsのDataFrameへ変換します。"""
        return records_to_polars(self.days)


class SecurityWeeklyMarginResponse(IRBankBaseModel):
    """東証週次信用残高APIの応答モデルです。"""

    security_code: str | None = None
    name: str | None = None
    industry_name: str | None = None
    issued_shares_count: int | None = None
    split_adjustment_status: str | None = None
    split_events: list[dict[str, Any]] = []
    exchange: str | None = None
    period: str | None = None
    fields: list[FieldInfo] = []
    weeks: list[dict[str, Any]] = []
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """週次信用残高データをpandasのDataFrameへ変換します。"""
        return records_to_pandas(self.weeks)

    def to_polars(self) -> pl.DataFrame:
        """週次信用残高データをpolarsのDataFrameへ変換します。"""
        return records_to_polars(self.weeks)
