from __future__ import annotations

from enum import Enum
from typing import Literal


class StrEnum(str, Enum):
    """文字列値を透過的に扱うEnum基底クラス"""

    def __str__(self) -> str:
        return str(self.value)


class Market(StrEnum):
    """東京証券取引所の市場区分"""

    PRIME = "Prime"
    STANDARD = "Standard"
    GROWTH = "Growth"


class Period(StrEnum):
    """財務情報および経営指標の期間種別"""

    ANNUAL = "annual"
    QUARTERLY = "quarterly"
    SEMIANNUAL = "semiannual"


class SegmentPeriod(StrEnum):
    """事業セグメント情報の期間種別"""

    ANNUAL = "annual"
    QUARTER = "quarter"


class RankingMetric(StrEnum):
    """市場ランキングの対象指標"""

    GAINERS = "gainers"
    LOSERS = "losers"
    VOLUME = "volume"


# 文字列リテラル型（IDE補完・型チェック用）
MarketType = Literal[
    "Prime",
    "Standard",
    "Growth",
    "プライム",
    "スタンダード",
    "グロース",
]

PeriodType = Literal["annual", "quarterly", "semiannual"]

SegmentPeriodType = Literal["annual", "quarter"]

RankingMetricType = Literal["gainers", "losers", "volume"]
