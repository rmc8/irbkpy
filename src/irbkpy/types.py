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


class Industry(StrEnum):
    """東証33業種区分"""

    FISHERY_AGRICULTURE = "水産・農林業"
    MINING = "鉱業"
    CONSTRUCTION = "建設業"
    FOODS = "食料品"
    TEXTILES_APPAREL = "繊維製品"
    PULP_PAPER = "パルプ・紙"
    CHEMICALS = "化学"
    PHARMACEUTICAL = "医薬品"
    OIL_COAL = "石油・石炭製品"
    RUBBER_PRODUCTS = "ゴム製品"
    GLASS_CERAMICS = "ガラス・土石製品"
    IRON_STEEL = "鉄鋼"
    NONFERROUS_METALS = "非鉄金属"
    METAL_PRODUCTS = "金属製品"
    MACHINERY = "機械"
    ELECTRIC_APPLIANCES = "電気機器"
    TRANSPORTATION_EQUIPMENT = "輸送用機器"
    PRECISION_INSTRUMENTS = "精密機器"
    OTHER_PRODUCTS = "その他製品"
    ELECTRIC_POWER_GAS = "電気・ガス業"
    LAND_TRANSPORTATION = "陸運業"
    MARINE_TRANSPORTATION = "海運業"
    AIR_TRANSPORTATION = "空運業"
    WAREHOUSING_HARBOR = "倉庫・運輸関連業"
    INFORMATION_COMMUNICATION = "情報・通信業"
    WHOLESALE_TRADE = "卸売業"
    RETAIL_TRADE = "小売業"
    BANKS = "銀行業"
    SECURITIES_COMMODITIES = "証券、商品先物取引業"
    INSURANCE = "保険業"
    OTHER_FINANCING = "その他金融業"
    REAL_ESTATE = "不動産業"
    SERVICES = "サービス業"


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


class SortOrder(StrEnum):
    """並び替え順序"""

    ASC = "asc"
    DESC = "desc"


class ListingStatus(StrEnum):
    """銘柄の上場状態"""

    ACTIVE = "active"
    DELISTED = "delisted"


class AccountingStandard(StrEnum):
    """会計基準"""

    JAPAN = "Japan"
    IFRS = "IFRS"
    US = "US"


# 文字列リテラル型（IDE補完・型チェック用）
MarketType = Literal[
    "Prime",
    "Standard",
    "Growth",
    "プライム",
    "スタンダード",
    "グロース",
]

IndustryType = Literal[
    "水産・農林業",
    "鉱業",
    "建設業",
    "食料品",
    "繊維製品",
    "パルプ・紙",
    "化学",
    "医薬品",
    "石油・石炭製品",
    "ゴム製品",
    "ガラス・土石製品",
    "鉄鋼",
    "非鉄金属",
    "金属製品",
    "機械",
    "電気機器",
    "輸送用機器",
    "精密機器",
    "その他製品",
    "電気・ガス業",
    "陸運業",
    "海運業",
    "空運業",
    "倉庫・運輸関連業",
    "情報・通信業",
    "卸売業",
    "小売業",
    "銀行業",
    "証券、商品先物取引業",
    "保険業",
    "その他金融業",
    "不動産業",
    "サービス業",
]

PeriodType = Literal["annual", "quarterly", "semiannual"]

SegmentPeriodType = Literal["annual", "quarter"]

RankingMetricType = Literal["gainers", "losers", "volume"]

SortOrderType = Literal["asc", "desc"]

ListingStatusType = Literal["active", "delisted"]

AccountingStandardType = Literal["Japan", "IFRS", "US"]
