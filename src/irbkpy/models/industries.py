from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Attribution, IRBankBaseModel
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class IndustryItem(IRBankBaseModel):
    """東証17業種（TOPIX-17）および33業種の個別区分情報です。"""

    code: str | None = None
    name: str | None = None
    classification: str | None = None
    parent: str | None = None


class IndustriesResponse(IRBankBaseModel):
    """東証17/33業種マスタAPI（GET /industries）の応答モデルです。"""

    industries: list[IndustryItem] = []
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """業種一覧データをpandasのDataFrameへ変換します。"""
        return records_to_pandas([i.model_dump() for i in self.industries])

    def to_polars(self) -> pl.DataFrame:
        """業種一覧データをpolarsのDataFrameへ変換します。"""
        return records_to_polars([i.model_dump() for i in self.industries])
