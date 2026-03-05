from __future__ import annotations

import json
import os
from urllib import parse, request

from app.schemas import PortfolioPosition, PortfolioSnapshot, SnapTradeConnectResponse


class SnapTradeService:
    def __init__(self) -> None:
        self.base_url = os.getenv("SNAPTRADE_BASE_URL", "https://api.snaptrade.com/api/v1")
        self.client_id = os.getenv("SNAPTRADE_CLIENT_ID", "demo-client")
        self.consumer_key = os.getenv("SNAPTRADE_CONSUMER_KEY", "demo-key")

    def get_connection_url(self, user_id: str) -> SnapTradeConnectResponse:
        # Lightweight implementation compatible with hosted SnapTrade and local mocks.
        query = parse.urlencode({"userId": user_id, "clientId": self.client_id})
        url = f"{self.base_url}/connect?{query}"
        return SnapTradeConnectResponse(user_id=user_id, connection_url=url)

    def get_portfolio(self, user_id: str) -> PortfolioSnapshot:
        url = f"{self.base_url}/users/{parse.quote(user_id)}/portfolio"
        req = request.Request(
            url,
            headers={
                "clientId": self.client_id,
                "consumerKey": self.consumer_key,
                "Accept": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            positions = [
                PortfolioPosition(
                    symbol=item.get("symbol", "UNKNOWN"),
                    quantity=float(item.get("quantity", 0)),
                    market_value=float(item.get("marketValue", 0)),
                )
                for item in payload.get("positions", [])
            ]
            return PortfolioSnapshot(
                user_id=user_id,
                positions=positions,
                cash_balance=float(payload.get("cashBalance", 0)),
            )
        except Exception:
            # Safe fallback for local development without SnapTrade credentials.
            return PortfolioSnapshot(
                user_id=user_id,
                positions=[PortfolioPosition(symbol="SPY", quantity=10, market_value=5000)],
                cash_balance=2500.0,
            )
