from __future__ import annotations

from .base import IRBankBaseModel


class UsageResponse(IRBankBaseModel):
    """API利用量ステータスの応答モデル

    当日のリクエスト上限、使用済み回数、残り回数、制限リセット時刻を保持します。
    """

    limit: int
    used: int
    remaining: int
    resets_at: str | None = None
