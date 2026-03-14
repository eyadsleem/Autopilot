"""
Stub client for interacting with the Kalshi API.

This client is intentionally minimal. It exposes a synchronous and an
asynchronous order placement method that returns a placeholder response.
In a real implementation this class would authenticate, maintain
connections to Kalshi's WebSocket feeds, and marshal order payloads via
HTTPS.
"""

from typing import Any, Dict, Optional


class KalshiClient:
    """
    A lightweight client stub for submitting orders to the Kalshi API.

    Parameters
    ----------
    base_url : str, optional
        Base URL for the API. Defaults to the production endpoint.
    api_key : str, optional
        API key or token for authenticated calls. Not used in the stub.
    """

    def __init__(self, base_url: str = "https://api.kalshi.com", api_key: Optional[str] = None) -> None:
        self.base_url = base_url
        self.api_key = api_key

    def place_order(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit an order payload synchronously.

        In this stub implementation, the payload is returned untouched
        with a status indicating that real connectivity is not yet
        implemented. In production this method would perform an HTTP
        request and return the parsed response.

        Parameters
        ----------
        order_payload :
            Dictionary containing the order parameters (ticker, side,
            count, price, client_order_id, etc.).

        Returns
        -------
        Dict[str, Any]
            A placeholder response containing the payload and status.
        """
        return {
            "status": "stub_not_implemented",
            "payload": order_payload,
        }

    async def place_order_async(self, order_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asynchronous variant of :meth:`place_order`.

        This method simply calls the synchronous version in the stub. In
        a real client it would perform an async HTTP call using an
        async‑compatible library (e.g. httpx).
        """
        return self.place_order(order_payload)
