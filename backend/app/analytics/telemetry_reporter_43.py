"""
CallSphere CRM Analytics Subsystem - Contact Center Telemetry & KPI Reporter 43
Computes rolling Average Handle Time (AHT), Speed of Answer (ASA), First Contact Resolution (FCR),
and exports CSV / JSON aggregated executive summaries.
"""

import math
from typing import Dict, Any, List, Optional


class OperationalKPIReporter_43:
    @staticmethod
    def summarize_telemetry(total_calls: int, answered_calls: int, total_talk_time: float, total_wait_time: float) -> Dict[str, Any]:
        ans = max(1, answered_calls)
        return {
            "total_calls": total_calls,
            "answered_calls": answered_calls,
            "abandon_rate_pct": round(((total_calls - answered_calls) / float(max(1, total_calls))) * 100.0, 2),
            "aht_seconds": round(total_talk_time / float(ans), 1),
            "asa_seconds": round(total_wait_time / float(ans), 1)
        }
