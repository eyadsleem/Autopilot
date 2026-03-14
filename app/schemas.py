from __future__ import annotations

from datetime import datetime
from importlib.util import find_spec
from typing import Literal

if find_spec("pydantic"):
    from pydantic import BaseModel, Field
else:
    class BaseModel:
        """Minimal model shim for environments without pydantic installed."""

        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    def Field(default=None, **_: object):
        return default


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class TechnicalIndicators(BaseModel):
    rsi_14: float | None = None
    macd: float | None = None
    macd_signal: float | None = None
    atr_14: float | None = None


class MarketSnapshot(BaseModel):
    symbol: str
    timeframe: str
    candles: list[Candle]
    indicators: TechnicalIndicators | None = None


class ChartAnalysis(BaseModel):
    trend: Literal["bullish", "bearish", "sideways"]
    confidence: float = Field(ge=0.0, le=1.0)
    patterns: list[str]
    key_levels: list[float]
    thesis: str
    suggested_entry: float | None = None
    suggested_stop_loss: float | None = None
    provider: str = "heuristic"


class SignalRequest(BaseModel):
    symbol: str
    current_price: float = Field(gt=0)
    support: float = Field(gt=0)
    resistance: float = Field(gt=0)
    risk_tolerance_pct: float = Field(gt=0, lt=10)
    account_balance: float = Field(gt=0)


class TradePlan(BaseModel):
    symbol: str
    direction: Literal["long", "short", "avoid"]
    entry: float
    stop_loss: float
    target: float
    risk_reward_ratio: float
    dollars_at_risk: float
    quantity: int
    rationale: str


class SnapTradeConnectResponse(BaseModel):
    user_id: str
    connection_url: str


class PortfolioPosition(BaseModel):
    symbol: str
    quantity: float
    market_value: float


class PortfolioSnapshot(BaseModel):
    user_id: str
    positions: list[PortfolioPosition]
    cash_balance: float


class AlertCreateRequest(BaseModel):
    symbol: str
    pattern: str
    channel: Literal["webhook", "email", "slack"]
    destination: str


class AlertRule(BaseModel):
    id: str
    symbol: str
    pattern: str
    channel: Literal["webhook", "email", "slack"]
    destination: str


class AlertTriggerRequest(BaseModel):
    symbol: str
    detected_patterns: list[str]


class AlertDispatchResult(BaseModel):
    alert_id: str
    delivered: bool
    channel: str
    destination: str
