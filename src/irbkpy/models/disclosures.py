from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class DisclosureMeta(IRBankBaseModel):
    """開示書類のメタデータモデル

    書類ID、書類種別、表題、提出日、開示日時、閲覧URL、PDFのURLを保持します。
    """

    doc_id: str
    source: str | None = None
    document_type: str | None = None
    title: str | None = None
    filing_date: str | None = None
    disclosed_at: str | None = None
    source_url: str | None = None
    pdf_url: str | None = None
    edinet_code: str | None = None
    available_for_redistribution_at: str | None = None


class DisclosuresListResponse(IRBankBaseModel):
    """開示書類一覧APIの応答モデル

    開示書類一覧および改ページ用のカーソルを保持します。
    """

    security_code: str | None = None
    edinet_code: str | None = None
    disclosures: list[DisclosureMeta] = []
    next_cursor: str | None = None
    reason: Reason | None = None
    attribution: Attribution | None = None

    def _to_records(self) -> list[dict[str, Any]]:
        """開示書類一覧を行辞書リストへ変換します。"""
        return [item.model_dump() for item in self.disclosures]

    def to_pandas(self) -> pd.DataFrame:
        """開示書類一覧をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self._to_records())

    def to_polars(self) -> pl.DataFrame:
        """開示書類一覧をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self._to_records())


class DisclosureDetailResponse(IRBankBaseModel):
    """開示書類詳細APIの応答モデル

    開示書類のメタデータ、抽出された各セクション本文、XBRLファクト、取得可能セクション一覧を保持します。
    """

    meta: DisclosureMeta | None = None
    sections: list[dict[str, Any]] = []
    xbrl_facts: dict[str, Any] = {}
    available_sections: list[str] = []
    attribution: Attribution | None = None


class DisclosureSectionResponse(IRBankBaseModel):
    """開示書類個別セクションAPIの応答モデル

    指定セクションのテキスト本文、セクション名、書類種別、提出日、閲覧URLを保持します。
    """

    section_text: str | None = None
    section_name: str | None = None
    document_type: str | None = None
    filing_date: str | None = None
    source_url: str | None = None
    pdf_url: str | None = None
    available_sections: list[str] = []
    attribution: Attribution | None = None
