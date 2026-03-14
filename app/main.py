from __future__ import annotations

import os

from fastapi import FastAPI, File, Header, HTTPException, UploadFile

from app.schemas import (
    AlertCreateRequest,
    AlertDispatchResult,
    AlertRule,
    AlertTriggerRequest,
    ChartAnalysis,
    MarketSnapshot,
    PortfolioSnapshot,
    SignalRequest,
    SnapTradeConnectResponse,
    TradePlan,
)
from app.services.alerts import AlertService
from app.services.chart_analyzer import ChartAnalyzer
from app.services.market_data import MarketDataService
from app.services.signal_engine import SignalEngine
from app.services.snaptrade import SnapTradeService

app = FastAPI(title="SnapTrader-style Decision Support API", version="0.2.0")
market_data = MarketDataService()
chart_analyzer = ChartAnalyzer()
signal_engine = SignalEngine()
snaptrade_service = SnapTradeService()
alert_service = AlertService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login")
def login(username: str, password: str) -> dict[str, str]:
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username/password required")
    token = os.getenv("DEMO_AUTH_TOKEN", "dev-token")
    return {"access_token": token, "token_type": "bearer"}


@app.get("/market/{symbol}", response_model=MarketSnapshot)
def get_market(symbol: str, interval: str = "1d", period: str = "3mo") -> MarketSnapshot:
    try:
        return market_data.get_snapshot(symbol=symbol, interval=interval, period=period)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/analyze-chart", response_model=ChartAnalysis)
async def analyze_chart(file: UploadFile = File(...)) -> ChartAnalysis:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    image_bytes = await file.read()
    try:
        return chart_analyzer.analyze(image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to process chart image: {exc}") from exc


@app.post("/trade-plan", response_model=TradePlan)
def generate_trade_plan(request: SignalRequest) -> TradePlan:
    return signal_engine.build_trade_plan(request)


@app.get("/snaptrade/connect/{user_id}", response_model=SnapTradeConnectResponse)
def snaptrade_connect(user_id: str, authorization: str | None = Header(default=None)) -> SnapTradeConnectResponse:
    _require_auth(authorization)
    return snaptrade_service.get_connection_url(user_id)


@app.get("/snaptrade/portfolio/{user_id}", response_model=PortfolioSnapshot)
def snaptrade_portfolio(user_id: str, authorization: str | None = Header(default=None)) -> PortfolioSnapshot:
    _require_auth(authorization)
    return snaptrade_service.get_portfolio(user_id)


@app.post("/alerts", response_model=AlertRule)
def create_alert(rule: AlertCreateRequest, authorization: str | None = Header(default=None)) -> AlertRule:
    _require_auth(authorization)
    return alert_service.create_rule(rule)


@app.get("/alerts", response_model=list[AlertRule])
def list_alerts(authorization: str | None = Header(default=None)) -> list[AlertRule]:
    _require_auth(authorization)
    return alert_service.list_rules()


@app.post("/alerts/trigger", response_model=list[AlertDispatchResult])
def trigger_alerts(request: AlertTriggerRequest, authorization: str | None = Header(default=None)) -> list[AlertDispatchResult]:
    _require_auth(authorization)
    return alert_service.trigger(request.symbol, request.detected_patterns)


def _require_auth(authorization: str | None) -> None:
    token = os.getenv("DEMO_AUTH_TOKEN", "dev-token")
    if authorization != f"Bearer {token}":
        raise HTTPException(status_code=401, detail="Unauthorized")
