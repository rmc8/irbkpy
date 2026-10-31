from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class RankingItem(IRBankBaseModel):
    """ランキング順位モデル

    順位、銘柄コード、企業名、業種名、終値、騰落率、売買高を保持します。
    """

    rank: int | None = None
    security_code: str
    name: str | None = None
    industry_name: str | None = None
    close_price: float | None = None
    change_percent: float | None = None
    volume: float | None = None


class RankingResponse(IRBankBaseModel):
    """ランキングAPIの応答モデル

    指標名、基準日、ランキング順位データ一覧を保持します。
    """

    metric: str
    target_date: str | None = None
    items: list[dict[str, Any]] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """ランキング結果をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self.items)

    def to_polars(self) -> pl.DataFrame:
        """ランキング結果をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self.items)
