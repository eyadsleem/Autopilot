from __future__ import annotations


def position_size(account_balance: float, risk_tolerance_pct: float, entry: float, stop_loss: float) -> tuple[float, int]:
    risk_budget = account_balance * (risk_tolerance_pct / 100)
    per_share_risk = abs(entry - stop_loss)
    if per_share_risk == 0:
        return risk_budget, 0

    qty = int(risk_budget // per_share_risk)
    return risk_budget, max(qty, 0)
