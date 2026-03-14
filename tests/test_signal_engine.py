from app.schemas import SignalRequest
from app.services.signal_engine import SignalEngine


def test_trade_plan_long_setup():
    engine = SignalEngine()
    req = SignalRequest(
        symbol="AAPL",
        current_price=190,
        support=180,
        resistance=210,
        risk_tolerance_pct=1,
        account_balance=10000,
    )

    plan = engine.build_trade_plan(req)

    assert plan.direction == "long"
    assert plan.quantity > 0
    assert plan.risk_reward_ratio > 1


def test_trade_plan_avoid_when_breaking_support():
    engine = SignalEngine()
    req = SignalRequest(
        symbol="AAPL",
        current_price=179,
        support=180,
        resistance=210,
        risk_tolerance_pct=1,
        account_balance=10000,
    )

    plan = engine.build_trade_plan(req)

    assert plan.direction == "avoid"
