"""
In‑memory market data cache.

The MarketCache stores snapshots of market order books. It can be
updated from a REST API or WebSocket feed and is used by the risk and
strategy layers to obtain pricing information. The cache does not
persist data; callers should implement persistence if necessary.
"""

from typing import Dict, Optional

from ..models import MarketBook


class MarketCache:
    """Simple in‑memory cache for market books."""

    def __init__(self) -> None:
        self.books: Dict[str, MarketBook] = {}

    def update(self, ticker: str, best_bid: Optional[int], best_ask: Optional[int], last_trade: Optional[int]) -> None:
        """
        Update or create a market book for the given ticker.

        Parameters
        ----------
        ticker : str
            The market ticker.
        best_bid : Optional[int]
            Highest bid price in cents.
        best_ask : Optional[int]
            Lowest ask price in cents.
        last_trade : Optional[int]
            Most recent trade price in cents.
        """
        book = self.books.get(ticker)
        if book is None:
            book = MarketBook(
                ticker=ticker,
                best_bid=best_bid,
                best_ask=best_ask,
                last_trade_price=last_trade,
            )
            self.books[ticker] = book
        else:
            book.best_bid = best_bid
            book.best_ask = best_ask
            book.last_trade_price = last_trade
            book.update_spread()

    def get(self, ticker: str) -> Optional[MarketBook]:
        """Return the cached book for a ticker, if available."""
        return self.books.get(ticker)
