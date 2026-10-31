from __future__ import annotations

from .base import Attribution, IRBankBaseModel


class Organization(IRBankBaseModel):
    """法人基本情報API（GET /organizations/{edinet_code}）の応答モデルです。

    法人名、所在地、上場証券コード一覧などを保持します。
    """

    edinet_code: str
    name_ja: str | None = None
    address_ja: str | None = None
    listed_security_codes: list[str] = []
    attribution: Attribution | None = None
