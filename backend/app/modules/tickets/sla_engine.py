from datetime import datetime, timezone, timedelta
from typing import Dict

def evaluate_sla_status(created_at: datetime, priority: str) -> Dict[str, any]:
    thresholds = {
        "CRITICAL": timedelta(minutes=15),
        "HIGH": timedelta(hours=1),
        "MEDIUM": timedelta(hours=4),
        "LOW": timedelta(hours=24)
    }
    limit = thresholds.get(priority.upper(), timedelta(hours=4))
    elapsed = datetime.now(timezone.utc) - created_at
    is_breached = elapsed > limit
    remaining_sec = max(0, int((limit - elapsed).total_seconds()))
    return {"is_breached": is_breached, "remaining_seconds": remaining_sec}
