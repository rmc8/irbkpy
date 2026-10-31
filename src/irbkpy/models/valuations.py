from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class ValuationRecord(IRBankBaseModel):
    """年度別の株価、PER、PBR、BPS、EPS、ROE、配当利回り、時価総額などのバリュエーション指標レコードです。"""

    fiscal_year: str | None = None
    stock_price: float | None = None
    stock_price_adjusted: float | None = None
    stock_price_high: float | None = None
    stock_price_high_adjusted: float | None = None
    stock_price_low: float | None = None
    stock_price_low_adjusted: float | None = None
    per: float | None = None
    per_source: str | None = None
    pbr: float | None = None
    pbr_adjusted: float | None = None
    bps: float | None = None
    bps_adjusted: float | None = None
    dps: float | None = None
    dps_adjusted: float | None = None
    eps: float | None = None
    eps_adjusted: float | None = None
    roe: float | None = None
    roe_computed: float | None = None
    dividend_yield: float | None = None
    dividend_yield_adjusted: float | None = None
    market_cap: float | None = None
    shares_outstanding: int | None = None


class ValuationsResponse(IRBankBaseModel):
    """年次バリュエーション時系列API（GET /valuations）の応答モデルです。"""

    security_code: str | None = None
    per_5y_avg: float | None = None
    fields: list[FieldInfo] = []
    history: list[ValuationRecord] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """バリュエーション時系列データをpandasのDataFrameへ変換します。"""
        return records_to_pandas([h.model_dump() for h in self.history])

    def to_polars(self) -> pl.DataFrame:
        """バリュエーション時系列データをpolarsのDataFrameへ変換します。"""
        return records_to_polars([h.model_dump() for h in self.history])
