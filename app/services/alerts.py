from __future__ import annotations

import json
import uuid
from urllib import request

from app.schemas import AlertCreateRequest, AlertDispatchResult, AlertRule


class AlertService:
    def __init__(self) -> None:
        self._rules: dict[str, AlertRule] = {}

    def create_rule(self, req: AlertCreateRequest) -> AlertRule:
        rule = AlertRule(
            id=str(uuid.uuid4()),
            symbol=req.symbol.upper(),
            pattern=req.pattern.lower(),
            channel=req.channel,
            destination=req.destination,
        )
        self._rules[rule.id] = rule
        return rule

    def list_rules(self) -> list[AlertRule]:
        return list(self._rules.values())

    def trigger(self, symbol: str, detected_patterns: list[str]) -> list[AlertDispatchResult]:
        normalized = {p.lower() for p in detected_patterns}
        results: list[AlertDispatchResult] = []

        for rule in self._rules.values():
            if rule.symbol != symbol.upper() or rule.pattern not in normalized:
                continue
            delivered = self._dispatch(rule, symbol, detected_patterns)
            results.append(
                AlertDispatchResult(
                    alert_id=rule.id,
                    delivered=delivered,
                    channel=rule.channel,
                    destination=rule.destination,
                )
            )
        return results

    def _dispatch(self, rule: AlertRule, symbol: str, patterns: list[str]) -> bool:
        message = {
            "symbol": symbol.upper(),
            "patterns": patterns,
            "alert_id": rule.id,
            "channel": rule.channel,
        }

        if rule.channel == "webhook":
            req = request.Request(
                rule.destination,
                method="POST",
                headers={"Content-Type": "application/json"},
                data=json.dumps(message).encode("utf-8"),
            )
            try:
                with request.urlopen(req, timeout=10):
                    return True
            except Exception:
                return False

        # email/slack are mocked for local MVP; swap with SES/SendGrid/Slack SDKs later.
        return True
