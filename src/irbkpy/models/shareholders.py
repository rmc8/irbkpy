from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, FieldInfo, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class Shareholder(IRBankBaseModel):
    """大株主の個別情報モデル

    株主名や持株比率、保有株式数、前期比率を保持します。
    """

    holder_name: str
    holding_ratio: float | None = None
    shares_held: int | None = None
    previous_ratio: float | None = None


class ShareholdersResponse(IRBankBaseModel):
    """大株主一覧APIの応答モデル

    対象銘柄における大株主の一覧および属性情報を保持します。
    """

    fields: list[FieldInfo] = []
    shareholders: list[Shareholder] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def _to_records(self) -> list[dict[str, Any]]:
        """大株主一覧を行辞書リストへ変換します。"""
        return [item.model_dump() for item in self.shareholders]

    def to_pandas(self) -> pd.DataFrame:
        """大株主一覧をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self._to_records())

    def to_polars(self) -> pl.DataFrame:
        """大株主一覧をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self._to_records())
