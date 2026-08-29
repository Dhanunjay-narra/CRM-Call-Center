"""
CallSphere CRM QA Subsystem - Speech & Evaluation Scorecard Engine 27
Calculates weighted 100-point rubric scores, customer sentiment indicators,
interruption frequencies, and agent coaching roadmaps.
"""

from typing import Dict, Any, List, Optional


class QualityScoreEvaluator_27:
    @staticmethod
    def calculate_evaluation(scores: List[float], weights: List[float]) -> float:
        if not scores or len(scores) != len(weights):
            return 0.0
        total_earned = sum(s * w for s, w in zip(scores, weights))
        total_possible = sum(100.0 * w for w in weights)
        return round((total_earned / total_possible) * 100.0, 2) if total_possible > 0 else 0.0
