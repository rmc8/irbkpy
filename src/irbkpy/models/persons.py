from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import Attribution, IRBankBaseModel, Reason
from .converters import records_to_pandas, records_to_polars

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl


class Appointment(IRBankBaseModel):
    """人物の就任履歴モデル

    就任先企業の銘柄コード、役職、社外役員フラグ、現任状況、任期を保持します。
    """

    security_code: str | None = None
    security_name: str | None = None
    role: str | None = None
    position: str | None = None
    latest_role: str | None = None
    latest_position: str | None = None
    is_outside: bool | None = None
    is_current: bool | None = None
    first_valid_from: str | None = None
    last_valid_to: str | None = None


class PersonProfile(IRBankBaseModel):
    """人物の基本情報モデル

    人物ID、氏名、生年月日、現任の役職一覧を保持します。
    """

    person_id: str
    name: str | None = None
    birth_date: str | None = None
    current_appointments: list[Appointment] = []
    attribution: Attribution | None = None


class PersonAppointmentsResponse(IRBankBaseModel):
    """就任履歴APIの応答モデル

    対象人物の全就任履歴を保持します。
    """

    person_id: str
    name: str | None = None
    appointments: list[Appointment] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def _to_records(self) -> list[dict[str, Any]]:
        """就任履歴を行辞書リストへ変換します。"""
        return [item.model_dump() for item in self.appointments]

    def to_pandas(self) -> pd.DataFrame:
        """就任履歴をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self._to_records())

    def to_polars(self) -> pl.DataFrame:
        """就任履歴をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self._to_records())


class CompensationRecord(IRBankBaseModel):
    """役員報酬の決算期別内訳モデル

    総額、固定報酬、業績連動報酬、株式報酬などの内訳を保持します。
    """

    fiscal_period_end: str | None = None
    total_comp: float | None = None
    fixed_comp: float | None = None
    performance_comp: float | None = None
    stock_comp: float | None = None


class CompanyCompensation(IRBankBaseModel):
    """企業別の役員報酬情報モデル

    企業ごとの役員報酬推移履歴を保持します。
    """

    security_code: str
    company_name: str | None = None
    history: list[CompensationRecord] = []


class PersonCompensationResponse(IRBankBaseModel):
    """役員報酬APIの応答モデル

    対象人物が各企業から受領した報酬の履歴を保持します。
    """

    person_id: str
    name: str | None = None
    companies: list[CompanyCompensation] = []
    reason: Reason | None = None
    attribution: Attribution | None = None


class ShareholdingRecord(IRBankBaseModel):
    """期別の株式保有状況モデル

    決算期末ごとの保有株式数や持株比率を保持します。
    """

    fiscal_period_end: str | None = None
    shares_held: int | None = None
    ownership_ratio: float | None = None


class CompanyHolding(IRBankBaseModel):
    """企業別の保有株式情報モデル

    企業ごとの保有株式数や保有比率の推移履歴を保持します。
    """

    security_code: str
    security_name: str | None = None
    is_current: bool | None = None
    latest_shares_held: int | None = None
    share_history: list[ShareholdingRecord] = []


class PersonHoldingsResponse(IRBankBaseModel):
    """役員保有株式APIの応答モデル

    対象人物による企業別保有株式の推移を保持します。
    """

    person_id: str
    holdings: list[CompanyHolding] = []
    reason: Reason | None = None
    attribution: Attribution | None = None


class Officer(IRBankBaseModel):
    """企業の個別役員モデル

    役員名、役職、社外役員フラグ、現任フラグ、次期候補フラグ、任期を保持します。
    """

    person_id: str | None = None
    name: str | None = None
    role: str | None = None
    position: str | None = None
    is_outside: bool | None = None
    is_current: bool | None = None
    is_next_term_nominee: bool | None = None
    first_valid_from: str | None = None
    last_valid_to: str | None = None


class OfficersResponse(IRBankBaseModel):
    """企業役員一覧APIの応答モデル

    特定企業に所属する役員の一覧を保持します。
    """

    security_code: str | None = None
    officers: list[Officer] = []
    reason: Reason | None = None
    attribution: Attribution | None = None

    def _to_records(self) -> list[dict[str, Any]]:
        """役員一覧を行辞書リストへ変換します。"""
        return [item.model_dump() for item in self.officers]

    def to_pandas(self) -> pd.DataFrame:
        """役員一覧をpandasのDataFrameに変換して返します。"""
        return records_to_pandas(self._to_records())

    def to_polars(self) -> pl.DataFrame:
        """役員一覧をpolarsのDataFrameに変換して返します。"""
        return records_to_polars(self._to_records())
