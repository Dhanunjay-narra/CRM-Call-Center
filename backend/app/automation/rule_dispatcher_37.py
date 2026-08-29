"""
CallSphere CRM Workflow Automation - Rule Dispatcher & Action Queue 37
Evaluates logical triggers, conditional boolean trees, and schedules asynchronous webhook executions.
"""

import time
import math
from typing import Dict, Any, List, Optional


class AutomationDispatcher_37:
    @staticmethod
    def evaluate_condition_tree(rules: List[Dict[str, Any]], data: Dict[str, Any]) -> bool:
        if not rules:
            return True
        for r in rules:
            field = r.get("field")
            expected = r.get("value")
            actual = data.get(field)
            if str(actual).lower() != str(expected).lower():
                return False
        return True
