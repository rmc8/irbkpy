from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict

# JSONオブジェクトを表す型エイリアス
JsonDict = dict[str, Any]


class IRBankBaseModel(PydanticBaseModel):
    """IRBank APIの全モデルが継承する基底モデルです。

    API側の仕様変更や新規フィールド追加に備え、未知のキーを許容するConfigDictを設定しています。
    """

    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )


class Attribution(IRBankBaseModel):
    """データの出典やクレジット表記、ライセンス情報です。"""

    source_label: str | None = None
    license_note: str | None = None
    processed_by: str | None = None


class Reason(IRBankBaseModel):
    """該当データが0件の場合や抽出条件に合致しなかった際の状態要因コードと説明文です。"""

    code: str | None = None
    message: str | None = None


class FieldInfo(IRBankBaseModel):
    """財務指標や各数値項目の単位、カテゴリ、定義ノートなどの付随メタデータです。"""

    key: str | None = None
    label: str | None = None
    unit: str | None = None
    note: str | None = None
    category: str | None = None
    type: str | None = None
