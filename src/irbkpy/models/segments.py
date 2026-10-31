from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class SegmentRecord(IRBankBaseModel):
    """事業セグメント別の売上高、営業利益、構成比率、前年同期比、従業員数などの業績レコードです。"""

    fiscal_year: str | None = None
    quarter: int | None = None
    segment_name: str | None = None
    revenue: float | None = None
    revenue_basis: str | None = None
    operating_income: float | None = None
    operating_income_basis: str | None = None
    share: float | None = None
    yoy: float | None = None
    employees: int | None = None
    assets: float | None = None


class SegmentsResponse(IRBankBaseModel):
    """セグメント別業績API（GET /segments）の応答モデルです。"""

    fields: list[FieldInfo] = []
    segments: list[SegmentRecord] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """セグメント別業績データをpandasのDataFrameへ変換します。"""
        return records_to_pandas([s.model_dump() for s in self.segments])

    def to_polars(self) -> pl.DataFrame:
        """セグメント別業績データをpolarsのDataFrameへ変換します。"""
        return records_to_polars([s.model_dump() for s in self.segments])
