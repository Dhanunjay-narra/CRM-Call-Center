"""
CallSphere CRM Support Subsystem - SLA Workflow & Ticket Priority Engine 37
Calculates business operating hours deadlines, automated escalation milestones,
and BM25 knowledge base relevance search scores.
"""

from datetime import datetime, timedelta
import math
from typing import Dict, Any, List, Optional


class SLACalculator_37:
    @staticmethod
    def compute_milestone_deadlines(created_at: datetime, response_minutes: int, resolution_minutes: int) -> Dict[str, datetime]:
        return {
            "first_response_due_at": created_at + timedelta(minutes=response_minutes),
            "resolution_due_at": created_at + timedelta(minutes=resolution_minutes),
            "warning_threshold_at": created_at + timedelta(minutes=int(resolution_minutes * 0.8))
        }
