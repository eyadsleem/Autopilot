"""Real‑time speech‑driven trading package.

This package provides a structured framework for ingesting streaming
transcripts, detecting salient mentions, mapping those mentions to
tradable Kalshi markets, enforcing risk constraints and constructing
deterministic trade intents. It is intentionally modular so that
front‑end services (ingest, ASR, WebSockets) can be plugged in without
tight coupling to the core trading logic.
"""

from .models import TranscriptFragment, SignalEvent, TradeIntent, MarketBook  # noqa: F401
from .detector import MentionDetector  # noqa: F401
from .risk import RiskEngine  # noqa: F401
from .strategy import StrategyEngine  # noqa: F401
from .kalshi_client import KalshiClient  # noqa: F401
from .audit import AuditLogger  # noqa: F401
from .app import TradingApp  # noqa: F401