from __future__ import annotations

from app.schemas import SignalRequest, TradePlan
from app.services.risk import position_size


class SignalEngine:
    def build_trade_plan(self, req: SignalRequest) -> TradePlan:
        long_rr = self._risk_reward(req.current_price, req.support, req.resistance)

        if req.current_price <= req.support:
            direction = "avoid"
            entry = req.current_price
            stop = req.support * 0.99
            target = req.resistance
            rationale = "Price is at/under support. Wait for confirmation before entering."
        else:
            direction = "long"
            entry = req.current_price
            stop = req.support * 0.99
            target = req.resistance
            rationale = "Long bias based on support/resistance structure and positive R:R."

        risk_budget, quantity = position_size(req.account_balance, req.risk_tolerance_pct, entry, stop)

        return TradePlan(
            symbol=req.symbol.upper(),
            direction=direction,
            entry=round(entry, 2),
            stop_loss=round(stop, 2),
            target=round(target, 2),
            risk_reward_ratio=round(long_rr, 2),
            dollars_at_risk=round(risk_budget, 2),
            quantity=quantity,
            rationale=rationale,
        )

    @staticmethod
    def _risk_reward(entry: float, stop: float, target: float) -> float:
        risk = abs(entry - stop)
        reward = abs(target - entry)
        if risk == 0:
            return 0.0
        return reward / risk
