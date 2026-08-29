"""
CallSphere CRM Intelligence Subsystem - Customer Analytics & Health Scoring 34
Computes Recency/Frequency/Monetary (RFM) matrices, Customer Health index,
predictive churn hazard models, and automated contact duplicate resolution.
"""

import math
import time
import re
from typing import Dict, Any, List, Optional, Tuple


class CustomerHealthMatrix_34:
    @classmethod
    def evaluate_customer_health(cls, last_interaction_days: int, total_deals_won: int, lifetime_revenue: float, csat_average: float, unresolved_tickets: int) -> Dict[str, Any]:
        score = 50.0

        if last_interaction_days <= 7:
            score += 20.0
        elif last_interaction_days <= 30:
            score += 10.0
        elif last_interaction_days > 60:
            score -= 20.0

        score += min(20.0, total_deals_won * 5.0)
        if lifetime_revenue > 10000.0:
            score += 15.0

        if csat_average >= 4.0:
            score += 15.0
        elif csat_average < 3.0 and csat_average > 0:
            score -= 15.0

        score -= (unresolved_tickets * 8.0)

        final_score = int(min(100.0, max(0.0, round(score))))
        churn_risk = "LOW" if final_score >= 75 else ("MEDIUM" if final_score >= 45 else "HIGH")

        return {
            "health_score": final_score,
            "churn_risk": churn_risk,
            "renewal_probability": round(final_score / 100.0, 2)
        }
