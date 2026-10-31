from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, IRBankBaseModel
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class ScreeningField(IRBankBaseModel):
    """スクリーニング対応項目モデル

    項目キー、表示名、単位、型区分（数値または列挙型）、説明文を保持します。
    """

    key: str
    label: str | None = None
    unit: str | None = None
    type: str | None = None
    note: str | None = None


class ScreeningFieldsResponse(IRBankBaseModel):
    """スクリーニング可能項目一覧APIの応答モデル

    利用可能なスクリーニング項目の定義一覧を保持します。
    """

    fields: list[ScreeningField] = []
    attribution: Attribution | None = None


class ScreenedMetric(IRBankBaseModel):
    """抽出された指標値モデル

    項目名、指標値、基準日を保持します。
    """

    field: str
    value: float | int | str | None = None
    as_of: str | None = None


class ScreenedSecurity(IRBankBaseModel):
    """スクリーニング結果の個別企業モデル

    銘柄コード、EDINETコード、企業名、抽出された各指標値を保持します。
    """

    security_code: str
    edinet_code: str | None = None
    name: str | None = None
    metrics: list[ScreenedMetric] = []


class ScreeningResponse(IRBankBaseModel):
    """スクリーニング検索APIの応答モデル

    条件に合致した銘柄一覧、総件数、改ページ用のカーソルを保持します。
    """

    securities: list[ScreenedSecurity] = []
    total_count: int | None = None
    next_cursor: str | None = None
    attribution: Attribution | None = None

    def _to_flat_records(self) -> list[dict[str, Any]]:
        """指標値を列展開したフラットな行辞書リストへ変換します。"""
        records = []
        for s in self.securities:
            row: dict[str, Any] = {
                "security_code": s.security_code,
                "edinet_code": s.edinet_code,
                "name": s.name,
            }
            for m in s.metrics:
                row[m.field] = m.value
            records.append(row)
        return records

    def to_pandas(self) -> pd.DataFrame:
        """スクリーニング結果をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self._to_flat_records())

    def to_polars(self) -> pl.DataFrame:
        """スクリーニング結果をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self._to_flat_records())
