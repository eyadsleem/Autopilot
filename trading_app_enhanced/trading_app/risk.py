"""
Risk controls for the trading application.

The RiskEngine acts as a gatekeeper before trade intents are sent to the
execution layer. It applies simple but essential checks on signal
confidence and market conditions (e.g. spread) and can be extended with
additional constraints such as max position sizing, daily loss limits and
cooldowns.
"""

from typing import Optional

from .models import SignalEvent, MarketBook


class RiskEngine:
    """
    A basic but extensible risk engine that governs whether trades may
    proceed. In addition to simple threshold checks on confidence and
    market spreads, the engine tracks exposure per market, enforces a
    maximum exposure cap, and provides a kill switch to halt trading.

    Parameters
    ----------
    max_contracts_per_order : int, optional
        Maximum number of contracts allowed in a single order. Default 25.
    max_spread_cents : int, optional
        Maximum allowed bid/ask spread in cents. Markets with wider spreads
        are rejected. Default 8.
    min_confidence : float, optional
        Minimum confidence required from the signal event. Default 0.82.
    max_exposure_per_market : int, optional
        Maximum total open exposure (in contracts) per market. If current
        exposure plus the proposed order size exceeds this value, the
        trade is blocked. Default 50.
    """

    def __init__(
        self,
        max_contracts_per_order: int = 25,
        max_spread_cents: int = 8,
        min_confidence: float = 0.82,
        max_exposure_per_market: int = 50,
    ) -> None:
        self.max_contracts_per_order = max_contracts_per_order
        self.max_spread_cents = max_spread_cents
        self.min_confidence = min_confidence
        self.max_exposure_per_market = max_exposure_per_market
        # Aggregate exposure by market ticker.
        self.exposure: dict[str, int] = {}
        # Optional kill switch that can be toggled to halt all trading.
        self.kill_switch: bool = False

    def allow(self, signal: SignalEvent, book: Optional[MarketBook], proposed_contracts: int = 1) -> bool:
        """
        Determine whether a signal and market meet the risk criteria.

        A signal is allowed if:
        - Trading is not globally disabled via the kill switch.
        - The signal confidence meets or exceeds ``min_confidence``.
        - A market book snapshot is available.
        - The market spread (ask minus bid) is within ``max_spread_cents``.
        - The proposed order does not exceed ``max_contracts_per_order``.
        - The current exposure plus proposed order size does not exceed
          ``max_exposure_per_market`` for that ticker.

        Parameters
        ----------
        signal : SignalEvent
            The detected signal event to evaluate.
        book : Optional[MarketBook]
            Current snapshot of the market book for the targeted ticker.
        proposed_contracts : int, optional
            Number of contracts in the proposed trade. Default 1.

        Returns
        -------
        bool
            True if the trade may proceed, False otherwise.
        """
        # Halt trading entirely if kill switch is engaged.
        if self.kill_switch:
            return False
        # Confidence threshold.
        if signal.confidence < self.min_confidence:
            return False
        # Must have a market book snapshot.
        if book is None:
            return False
        # Spread check (bid/ask must be defined and within threshold).
        spread = book.spread_cents
        if spread is None or spread > self.max_spread_cents:
            return False
        # Per-order contract limit.
        if proposed_contracts > self.max_contracts_per_order:
            return False
        # Exposure check: ensure we will not exceed the max exposure per market.
        current_exp = self.exposure.get(book.ticker, 0)
        if current_exp + proposed_contracts > self.max_exposure_per_market:
            return False
        return True

    def record_trade(self, ticker: str, contracts: int) -> None:
        """
        Record an executed trade to update exposure.

        Parameters
        ----------
        ticker : str
            The market ticker traded.
        contracts : int
            Number of contracts executed. Positive values increase
            exposure; negative values decrease exposure (e.g. when
            flattening or closing positions).
        """
        self.exposure[ticker] = self.exposure.get(ticker, 0) + contracts
        # Clamp exposure to zero if it goes negative (e.g. after flattening).
        if self.exposure[ticker] < 0:
            self.exposure[ticker] = 0

    def toggle_kill_switch(self, enabled: bool) -> None:
        """Enable or disable the kill switch. When enabled, all trades are blocked."""
        self.kill_switch = enabled
