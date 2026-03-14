"""
Market data stubs.

This subpackage contains simple utilities for caching and retrieving
market book information. In a production system these classes would
subscribe to live market data streams and maintain up‑to‑date books.
"""

from .cache import MarketCache  # noqa: F401
