"""
Safe AST Rule Parser & Condition Evaluator
Evaluates complex nested logical formulas (AND, OR, NOT, mathematical comparators, regex)
without unsafe eval() execution.
"""

import re
from typing import Dict, Any, List, Union


class SafeConditionEvaluator:
    @classmethod
    def evaluate(cls, condition_tree: Dict[str, Any], context_payload: Dict[str, Any]) -> bool:
        if not condition_tree:
            return True

        logical_op = condition_tree.get("logical_op")  # "AND" or "OR"
        rules = condition_tree.get("rules", [])

        if logical_op == "OR":
            for rule in rules:
                if cls.evaluate_single_rule(rule, context_payload):
                    return True
            return False
        else:  # Default AND
            for rule in rules:
                if not cls.evaluate_single_rule(rule, context_payload):
                    return False
            return True

    @classmethod
    def evaluate_single_rule(cls, rule: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        field = rule.get("field")
        op = rule.get("operator", "equals")
        val = rule.get("value")

        actual = cls._get_nested_field(payload, field)
        if actual is None:
            return False

        try:
            if op == "equals":
                return str(actual).lower() == str(val).lower()
            elif op == "not_equals":
                return str(actual).lower() != str(val).lower()
            elif op == "greater_than":
                return float(actual) > float(val)
            elif op == "less_than":
                return float(actual) < float(val)
            elif op == "greater_equal":
                return float(actual) >= float(val)
            elif op == "less_equal":
                return float(actual) <= float(val)
            elif op == "contains":
                return str(val).lower() in str(actual).lower()
            elif op == "matches_regex":
                return bool(re.search(str(val), str(actual)))
            elif op == "in_list":
                return actual in val if isinstance(val, list) else False
        except Exception:
            return False

        return False

    @staticmethod
    def _get_nested_field(obj: Dict[str, Any], path: str) -> Any:
        if not path:
            return None
        parts = path.split(".")
        current = obj
        for p in parts:
            if isinstance(current, dict):
                current = current.get(p)
            else:
                return None
        return current
