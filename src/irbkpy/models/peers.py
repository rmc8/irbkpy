from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Attribution, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class ParentCompany(IRBankBaseModel):
    """競合企業が属する親会社等の情報（名称、証券コード、関係種別、議決権割合）です。"""

    name: str | None = None
    security_code: str | None = None
    relation_type: str | None = None
    voting_ratio: float | None = None


class PeerCompany(IRBankBaseModel):
    """有価証券報告書の分析に基づく競合企業の詳細情報です。"""

    security_code: str
    name: str | None = None
    industry: str | None = None
    segments: list[str] = []
    competition_reason: str | None = None
    capital_relationship: str | None = None
    parent_companies: list[ParentCompany] = []


class PeersResponse(IRBankBaseModel):
    """競合企業API（GET /peers）の応答モデルです。"""

    security_code: str | None = None
    peers: list[PeerCompany] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def to_pandas(self) -> pd.DataFrame:
        """競合企業一覧データをpandasのDataFrameへ変換します。"""
        return records_to_pandas([p.model_dump() for p in self.peers])

    def to_polars(self) -> pl.DataFrame:
        """競合企業一覧データをpolarsのDataFrameへ変換します。"""
        return records_to_polars([p.model_dump() for p in self.peers])
