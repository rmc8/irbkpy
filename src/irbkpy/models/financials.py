from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class FinancialPeriod(IRBankBaseModel):
    """決算期ごとの財務諸表概要データです。"""

    fiscal_year: str | None = None
    quarter: str | None = None
    accounting_standard: str | None = None
    is_consolidated: bool | None = None


class FinancialsResponse(IRBankBaseModel):
    """財務時系列API（GET /financials）の応答モデルです。"""

    edinet_code: str | None = None
    fields: list[FieldInfo] = []
    periods: list[dict[str, Any]] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """財務時系列データをpandasのDataFrameへ変換します。"""
        return records_to_pandas(self.periods)

    def to_polars(self) -> pl.DataFrame:
        """財務時系列データをpolarsのDataFrameへ変換します。"""
        return records_to_polars(self.periods)


class IndicatorsResponse(IRBankBaseModel):
    """計算済み財務指標時系列API（GET /indicators）の応答モデルです。"""

    edinet_code: str | None = None
    fields: list[FieldInfo] = []
    periods: list[dict[str, Any]] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """財務指標時系列データをpandasのDataFrameへ変換します。"""
        return records_to_pandas(self.periods)

    def to_polars(self) -> pl.DataFrame:
        """財務指標時系列データをpolarsのDataFrameへ変換します。"""
        return records_to_polars(self.periods)
