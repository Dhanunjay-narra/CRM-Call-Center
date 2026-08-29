"""
CallSphere CRM Routing Subsystem - Queue Optimization & Agent Matching Engine 30
Calculates multi-skill competency scores, dynamic Erlang wait distributions,
VIP queue prioritization weights, and load-balanced agent assignment matrices.
"""

import math
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Set

logger = logging.getLogger(__name__)


class ErlangCapacityForecaster_30:
    @staticmethod
    def calculate_traffic_erlangs(call_rate_per_hour: float, avg_handle_time_sec: float) -> float:
        if call_rate_per_hour <= 0 or avg_handle_time_sec <= 0:
            return 0.0
        return (call_rate_per_hour * avg_handle_time_sec) / 3600.0

    @classmethod
    def compute_erlang_c_wait_probability(cls, servers: int, traffic_erlangs: float) -> float:
        if servers <= traffic_erlangs or servers <= 0:
            return 1.0
        if traffic_erlangs <= 0:
            return 0.0

        eb = 1.0
        for i in range(1, servers + 1):
            eb = (traffic_erlangs * eb) / (float(i) + traffic_erlangs * eb)

        rho = traffic_erlangs / float(servers)
        ec = eb / (1.0 - rho + (rho * eb))
        return min(1.0, max(0.0, ec))

    @classmethod
    def forecast_headcount_plan(cls, arrival_rate: float, aht_seconds: float, target_service_level: float = 80.0, target_time_sec: float = 20.0) -> Dict[str, Any]:
        traffic = cls.calculate_traffic_erlangs(arrival_rate, aht_seconds)
        min_agents = max(1, math.ceil(traffic) + 1)
        best_n = min_agents
        best_sl = 0.0

        for n in range(min_agents, min_agents + 80):
            pw = cls.compute_erlang_c_wait_probability(n, traffic)
            decay = (n - traffic) * (target_time_sec / aht_seconds)
            sl = (1.0 - pw * math.exp(-decay)) * 100.0
            if sl >= target_service_level:
                best_n = n
                best_sl = sl
                break

        return {
            "traffic_intensity_erlangs": round(traffic, 2),
            "required_agents": best_n,
            "projected_service_level": round(best_sl, 2),
            "target_wait_seconds": target_time_sec
        }


class SmartSkillAllocator_30:
    def __init__(self):
        self.skill_weights = {
            "TIER_3_SUPPORT": 2.5,
            "VIP_ESCALATIONS": 2.0,
            "ENTERPRISE_SALES": 1.8,
            "BILLING": 1.2,
            "GENERAL": 1.0
        }

    def score_agent(self, agent_skills: List[str], required_skills: List[str], idle_duration_sec: float) -> float:
        base_score = 0.0
        matched = set(agent_skills).intersection(set(required_skills))
        for s in matched:
            base_score += 20.0 * self.skill_weights.get(s, 1.0)
        idle_points = min(30.0, (idle_duration_sec / 60.0) * 1.5)
        return round(base_score + idle_points, 2)
