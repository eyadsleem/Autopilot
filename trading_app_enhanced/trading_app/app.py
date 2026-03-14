"""
Top‑level orchestrator for the trading pipeline.

The TradingApp glues together the mention detector, risk engine,
strategy, market cache and execution client. It exposes a coroutine to
process individual TranscriptFragment instances. In a production
deployment this orchestrator would run as part of an event loop, fed by
audio ingestion and ASR components.
"""

import asyncio
from typing import Optional

from .detector import MentionDetector
from .risk import RiskEngine
from .strategy import StrategyEngine, MARKET_MAP
from .kalshi_client import KalshiClient
from .market.cache import MarketCache
from .models import TranscriptFragment
from .audit import AuditLogger


class TradingApp:
    """Orchestrate mention detection, risk checks, strategy and execution."""

    def __init__(self) -> None:
        self.detector = MentionDetector()
        self.risk = RiskEngine()
        self.strategy = StrategyEngine()
        self.market_cache = MarketCache()
        self.executor = KalshiClient()
        self.audit = AuditLogger()

    async def process_fragment(self, fragment: TranscriptFragment) -> None:
        """
        Process a single transcript fragment.

        If a signal is detected and passes risk checks, construct a trade
        intent and submit it via the execution client. The result of the
        order submission is not persisted but is printed to stdout for
        demonstration purposes.
        """
        # Audit the incoming fragment before any processing.
        self.audit.log_fragment(fragment)
        signal = self.detector.process(fragment)
        if signal is None:
            return
        # Audit the detected signal event.
        self.audit.log_signal(signal)
        # Iterate over mapped markets for this event class.
        for ticker in MARKET_MAP.get(signal.event_class, []):
            book = self.market_cache.get(ticker)
            # Determine the number of contracts the strategy intends to trade.
            # Build a tentative intent first so we can perform risk checks using the size.
            tentative_intent = self.strategy.build_trade_intent(signal, ticker, book)
            if tentative_intent is None:
                continue
            contracts = tentative_intent.contracts
            # Evaluate risk using the proposed contract size.
            if not self.risk.allow(signal, book, proposed_contracts=contracts):
                continue
            # Audit the trade intent before execution.
            self.audit.log_intent(tentative_intent)
            # Build order payload following Kalshi API structure.
            payload = {
                "ticker": tentative_intent.market_ticker,
                "side": tentative_intent.side,
                "count": tentative_intent.contracts,
                "price": tentative_intent.limit_price_cents,
                "client_order_id": f"{tentative_intent.event_id}-{tentative_intent.market_ticker}",
            }
            # Submit order asynchronously and print result.
            result = await self.executor.place_order_async(payload)
            print("Submitted", payload, "->", result)
            # Audit the execution result.
            self.audit.log_execution(result)
            # Record the trade in the risk engine to update exposure. Assume only buy orders increase exposure.
            # For simplicity we treat all trades as increasing exposure; in a real system we would handle
            # sell/closing orders differently.
            self.risk.record_trade(ticker, contracts)
