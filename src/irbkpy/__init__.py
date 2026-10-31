from __future__ import annotations

from .client import AsyncIRBankClient, IRBankClient
from .exceptions import (
    AuthenticationError,
    BadRequestError,
    ForbiddenError,
    IRBankAPIError,
    IRBankError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .models import *
from .types import (
    Market,
    MarketType,
    Period,
    PeriodType,
    RankingMetric,
    RankingMetricType,
    SegmentPeriod,
    SegmentPeriodType,
)

__version__ = "0.1.1"

__all__ = [
    "AsyncIRBankClient",
    "AuthenticationError",
    "BadRequestError",
    "ForbiddenError",
    "IRBankAPIError",
    "IRBankClient",
    "IRBankError",
    "Market",
    "MarketType",
    "NotFoundError",
    "Period",
    "PeriodType",
    "RankingMetric",
    "RankingMetricType",
    "RateLimitError",
    "SegmentPeriod",
    "SegmentPeriodType",
    "ServerError",
    "__version__",
]
