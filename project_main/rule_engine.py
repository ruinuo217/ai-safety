"""
rule_engine.py -- 規則引擎

職責：
  載入 rules.yaml → 接收 YOLO Event JSON →
  比對規則條件 → 產出觸發的規則與對應 severity / action
"""

import os
import yaml


RULES_PATH = os.path.join(os.path.dirname(__file__), "rules.yaml")


def load_rules(path: str = RULES_PATH) -> list:
    """載入 rules.yaml"""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("rules", [])


def evaluate_event(event: dict, rules: list = None) -> list:
    """
    評估 YOLO Event JSON，回傳所有觸發的規則

    回傳：
    [
        {
            "rule_name": "multiple_no_helmet",
            "description": "多人未戴安全帽（3人以上）",
            "severity": "high",
            "action": "alert_and_escalate"
        }
    ]
    """
    if rules is None:
        rules = load_rules()

    no_helmet = event.get("no_helmet_count", 0)
    helmet = event.get("helmet_count", 0)
    total = no_helmet + helmet
    ratio = no_helmet / total if total > 0 else 0

    triggered = []
    for rule in rules:
        cond = rule.get("condition", {})
        match = True

        for key, expr in cond.items():
            if key == "no_helmet_count":
                if not _eval_condition(no_helmet, expr):
                    match = False
            elif key == "violation_ratio":
                if not _eval_condition(ratio, expr):
                    match = False

        if match:
            triggered.append({
                "rule_name": rule["name"],
                "description": rule["description"],
                "severity": rule["severity"],
                "action": rule["action"],
            })

    return triggered


def get_highest_severity(triggered: list) -> str:
    """取得最高嚴重程度"""
    order = {"info": 0, "medium": 1, "high": 2}
    if not triggered:
        return "info"
    return max(triggered, key=lambda r: order.get(r["severity"], 0))["severity"]


def _eval_condition(value: float, expr: str) -> bool:
    """評估簡單條件表達式，如 '>= 3'"""
    expr = expr.strip()
    if expr.startswith(">="):
        return value >= float(expr[2:].strip())
    elif expr.startswith(">"):
        return value > float(expr[1:].strip())
    elif expr.startswith("<="):
        return value <= float(expr[2:].strip())
    elif expr.startswith("<"):
        return value < float(expr[1:].strip())
    elif expr.startswith("=="):
        return value == float(expr[2:].strip())
    return False
