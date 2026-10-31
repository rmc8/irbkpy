from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class DividendRecord(IRBankBaseModel):
    """年度別1株当たり配当金、配当性向、DOE、連続増配年数などの配当実績レコードです。"""

    fiscal_year: int | None = None
    annual_dps: float | None = None
    annual_dps_adjusted: float | None = None
    payout_ratio: float | None = None
    doe: float | None = None
    net_asset_dividend_ratio: float | None = None
    consecutive_growth_years: int | None = None
    source_refs: list[dict[str, Any]] = []


class DividendsResponse(IRBankBaseModel):
    """年次配当実績API（GET /dividends）の応答モデルです。"""

    edinet_code: str | None = None
    security_code: str | None = None
    fields: list[FieldInfo] = []
    records: list[DividendRecord] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """配当実績データをpandasのDataFrameへ変換します。"""
        return records_to_pandas([r.model_dump() for r in self.records])

    def to_polars(self) -> pl.DataFrame:
        """配当実績データをpolarsのDataFrameへ変換します。"""
        return records_to_polars([r.model_dump() for r in self.records])
