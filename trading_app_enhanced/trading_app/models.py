"""
Dataclasses representing the core domain entities used by the trading
application. These models capture the structure of streaming transcript
fragments, detected signal events, and the resulting trade intents.

The aim of these dataclasses is to provide a clear and type‑safe
representation of the data flowing through the system. They can be
serialized for logging, storage or transmission across services and are
intentionally minimal – additional metadata can always be wrapped in
custom structures upstream.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Literal


@dataclass
class TranscriptFragment:
    """
    Represents a fragment of text emitted by a streaming ASR engine.

    Each fragment covers a contiguous time range of audio from a single
    source. Partial fragments may be revised by subsequent final fragments
    (see `revision_of`), and consumers should use `is_final` to decide
    whether a fragment should be considered authoritative.
    """

    # Identifier for the feed or source of this fragment (e.g. “fed_hearing_1”).
    source_id: str
    # Unique identifier for this fragment within the feed.
    fragment_id: str
    # Raw transcript text for this fragment.
    text: str
    # Start timestamp of the audio segment (seconds since epoch).
    audio_start_ts: float
    # End timestamp of the audio segment (seconds since epoch).
    audio_end_ts: float
    # When this fragment was received/ingested (seconds since epoch).
    received_ts: float
    # Confidence score provided by the ASR (0.0 – 1.0).
    confidence: float
    # Whether this fragment is final (true) or subject to later revision (false).
    is_final: bool
    # Optional speaker label associated with this fragment.
    speaker: Optional[str] = None
    # If this fragment is a revision, reference to the fragment it supersedes.
    revision_of: Optional[str] = None


@dataclass
class SignalEvent:
    """
    Represents a salient event detected from a rolling window of transcript
    fragments. Signal events are provisional if derived from partial
    transcripts and should be treated with appropriate caution by the
    strategy and risk layers.
    """

    event_id: str
    # The feed/source identifier (matches TranscriptFragment.source_id).
    source_id: str
    # Class of the event (e.g. “hawkish_rate_signal”).
    event_class: str
    # Concatenated text window surrounding the event detection.
    text_window: str
    # Confidence associated with the underlying transcript fragment.
    confidence: float
    # Timestamp when the event was detected (seconds since epoch).
    detected_ts: float
    # True if derived from a partial transcript, False if final.
    is_provisional: bool
    # Speaker associated with the detected phrase, if any.
    speaker: Optional[str] = None
    # List of matched patterns/terms that triggered this event.
    trigger_terms: Optional[List[str]] = field(default_factory=list)


@dataclass
class TradeIntent:
    """
    Describes an intended order derived from a signal event and market data.

    This structure does not itself place an order – it simply captures the
    parameters that an execution engine should use when submitting to the
    Kalshi API (ticker, side, size, price, reason).
    """

    event_id: str
    # Market ticker on Kalshi.
    market_ticker: str
    # Direction and contract type (e.g. “buy_yes”, “sell_no”).
    side: str
    # Quantity of contracts to trade.
    contracts: int
    # Limit price in cents (0–99).
    limit_price_cents: int
    # Encoded reason or strategy code for auditability.
    reason_code: str
    # When this intent was created (seconds since epoch).
    created_ts: float


@dataclass
class MarketBook:
    """
    Simple representation of a market’s order book snapshot.

    Only the minimal fields required for simple risk checks and pricing
    decisions are included here. If either `best_bid` or `best_ask` is
    None, the spread is set to None.
    """

    ticker: str
    best_bid: Optional[int] = None  # highest bid price in cents
    best_ask: Optional[int] = None  # lowest ask price in cents
    last_trade_price: Optional[int] = None  # last trade price in cents
    # Spread is computed dynamically; do not initialise directly.
    spread_cents: Optional[int] = field(init=False, default=None)

    def __post_init__(self) -> None:
        """Compute the initial spread after construction."""
        self.update_spread()

    def update_spread(self) -> None:
        """Recompute the spread (best ask minus best bid) in cents."""
        if self.best_bid is not None and self.best_ask is not None:
            self.spread_cents = self.best_ask - self.best_bid
        else:
            self.spread_cents = None
