from app.schemas import AlertCreateRequest
from app.services.alerts import AlertService


def test_alert_rule_create_and_trigger_email_channel():
    service = AlertService()
    rule = service.create_rule(
        AlertCreateRequest(
            symbol="AAPL",
            pattern="ascending channel",
            channel="email",
            destination="trader@example.com",
        )
    )

    triggered = service.trigger("AAPL", ["ascending channel", "higher highs"])

    assert rule.id in [item.alert_id for item in triggered]
    assert triggered[0].delivered is True
