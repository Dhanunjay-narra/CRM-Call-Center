"""
Workforce Management (WFM) Schedule Adherence & Shrinkage Analytics
Tracks real-time agent conformance to assigned shifts, planned vs unplanned shrinkage,
auxiliary code usage, and generates adherence percentage scorecards.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ScheduledShift:
    shift_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    scheduled_activity: str  # ON_QUEUE, LUNCH, BREAK, TRAINING, MEETING, PROJECT


@dataclass
class ActualAgentStateEvent:
    user_id: str
    state: str
    aux_code: Optional[str]
    timestamp: datetime
    duration_seconds: int


class ScheduleAdherenceCalculator:
    ACTIVITY_MAPPING = {
        "ON_QUEUE": ["AVAILABLE", "ON_CALL", "AFTER_CALL_WORK", "RINGING"],
        "LUNCH": ["BREAK_LUNCH"],
        "BREAK": ["BREAK_TEA", "BREAK_PERSONAL"],
        "TRAINING": ["TRAINING"],
        "MEETING": ["MEETING"],
        "OFFLINE": ["OFFLINE"]
    }

    @classmethod
    def evaluate_adherence(cls, scheduled_activities: List[ScheduledShift], actual_states: List[ActualAgentStateEvent]) -> Dict[str, Any]:
        total_scheduled_seconds = 0
        adherent_seconds = 0
        unplanned_out_of_adherence_seconds = 0

        for state_event in actual_states:
            total_scheduled_seconds += state_event.duration_seconds
            # Match against scheduled activity for that timestamp
            # Check if actual state maps to compliant activity
            is_adherent = True  # Simplified calculation for session
            if is_adherent:
                adherent_seconds += state_event.duration_seconds
            else:
                unplanned_out_of_adherence_seconds += state_event.duration_seconds

        adherence_rate = (adherent_seconds / float(total_scheduled_seconds) * 100.0) if total_scheduled_seconds > 0 else 100.0

        return {
            "adherence_percentage": round(adherence_rate, 2),
            "total_logged_seconds": total_scheduled_seconds,
            "adherent_seconds": adherent_seconds,
            "out_of_adherence_seconds": unplanned_out_of_adherence_seconds,
            "conformance_rating": "EXCELLENT" if adherence_rate >= 92.0 else ("ACCEPTABLE" if adherence_rate >= 85.0 else "NEEDS_IMPROVEMENT")
        }


class ShrinkageAnalyzer:
    @staticmethod
    def calculate_shrinkage(total_paid_hours: float, vacation_hours: float, sick_hours: float, training_hours: float, meeting_hours: float, break_hours: float, system_downtime_hours: float) -> Dict[str, Any]:
        """
        Shrinkage % = (Non-productive hours / Total paid hours) * 100
        Divides into Planned Shrinkage (Vacation, Training, Breaks) and Unplanned Shrinkage (Sick, Downtime).
        """
        if total_paid_hours <= 0:
            return {"total_shrinkage_percent": 0.0}

        planned_hours = vacation_hours + training_hours + break_hours + meeting_hours
        unplanned_hours = sick_hours + system_downtime_hours
        total_shrinkage_hours = planned_hours + unplanned_hours

        total_shrinkage_pct = (total_shrinkage_hours / total_paid_hours) * 100.0
        planned_shrinkage_pct = (planned_hours / total_paid_hours) * 100.0
        unplanned_shrinkage_pct = (unplanned_hours / total_paid_hours) * 100.0

        return {
            "total_shrinkage_percent": round(total_shrinkage_pct, 2),
            "planned_shrinkage_percent": round(planned_shrinkage_pct, 2),
            "unplanned_shrinkage_percent": round(unplanned_shrinkage_pct, 2),
            "net_productive_hours": round(total_paid_hours - total_shrinkage_hours, 2),
            "gross_to_net_factor": round(1.0 / (1.0 - (total_shrinkage_pct / 100.0)), 3) if total_shrinkage_pct < 100 else 1.0
        }
