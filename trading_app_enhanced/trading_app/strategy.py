"""
Deterministic strategy engine and market mapping.

This module provides a simple mapping from detected event classes to one
or more tradable Kalshi market tickers. The StrategyEngine uses this
mapping along with market book information to construct a TradeIntent
whenever a signal passes risk checks.
"""

import time
from typing import Dict, List, Optional

from .models import SignalEvent, TradeIntent, MarketBook


# Hard‑coded mapping from event class to list of candidate Kalshi tickers.
# In a more advanced system this would likely be loaded from a
# configuration file or database.
MARKET_MAP: Dict[str, List[str]] = {
    "hawkish_rate_signal": ["FED-PRIMARY-001"],
    "shutdown_avoided_signal": ["GOVSHUT-PRIMARY-001"],
    "nominee_support_signal": ["CONFIRM-PRIMARY-001"],
}


class StrategyEngine:
    """
    Determine how to translate signals into trade intents given market data.

    The engine is deliberately straightforward: it computes a fair price
    from the current book snapshot (midpoint of best bid/ask if both are
    known) and then constructs a limit order slightly inside the spread
    favouring an aggressive fill. Side, size and price logic can be
    extended or replaced as strategies evolve.
    """

    def build_trade_intent(
        self, signal: SignalEvent, market_ticker: str, book: Optional[MarketBook]
    ) -> Optional[TradeIntent]:
        """
        Construct a TradeIntent for a given signal and market book.

        Parameters
        ----------
        signal :
            The detected signal event.
        market_ticker :
            The Kalshi ticker to trade.
        book :
            Current snapshot of the market book for pricing.

        Returns
        -------
        Optional[TradeIntent]
            A populated trade intent if pricing is possible; otherwise None.
        """
        # Compute mid price: use 50 if we do not have both sides of the book.
        if book is not None and book.best_bid is not None and book.best_ask is not None:
            mid = (book.best_bid + book.best_ask) // 2
        else:
            mid = 50

        # Determine the side based on the event class; default to buy_yes.
        # Sophisticated strategies might choose sell_yes/sell_no etc.
        side = "buy_yes"

        # Place order slightly inside the offer to maximise the chance of fill.
        price = min(mid + 1, 99)

        # Use a fixed contract size; future implementations could vary this.
        contracts = 10

        return TradeIntent(
            event_id=signal.event_id,
            market_ticker=market_ticker,
            side=side,
            contracts=contracts,
            limit_price_cents=price,
            reason_code=f"{signal.event_class}_{signal.confidence:.2f}",
            created_ts=time.time(),
        )
