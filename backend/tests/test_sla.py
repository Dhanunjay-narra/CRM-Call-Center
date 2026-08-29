from datetime import datetime, timezone, timedelta
from app.modules.tickets.sla_engine import evaluate_sla_status

def test_sla_breach_detection():
    now = datetime.now(timezone.utc)
    res_ok = evaluate_sla_status(now - timedelta(minutes=5), "CRITICAL")
    assert res_ok["is_breached"] is False
    
    res_breach = evaluate_sla_status(now - timedelta(minutes=20), "CRITICAL")
    assert res_breach["is_breached"] is True
