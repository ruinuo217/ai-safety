"""
workflow.py -- LangGraph StateGraph 告警處理工作流

職責：
  接收 YOLO Event JSON → Rule Engine 風險分級 →
  LangGraph StateGraph 實作：
    1. 高/低風險條件分流
    2. 最多 3 次重試迴圈（LLM 分析失敗時自動重試）
    3. Human-in-the-Loop 主管審核（高風險事件）
    4. LLM 生成告警訊息與摘要

技術：LangGraph StateGraph, LangChain, Gemini API
"""

import os
from datetime import datetime
from typing import Literal
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing_extensions import TypedDict

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
parser = StrOutputParser()


# ============================================================
# State 定義
# ============================================================
class AlertState(TypedDict):
    """StateGraph 流轉狀態"""
    event: dict                # YOLO Event JSON
    risk_level: str            # high / low
    analysis: str              # LLM 分析結果
    alert_message: str         # 告警訊息
    retry_count: int           # 重試次數
    max_retries: int           # 最大重試次數
    needs_review: bool         # 是否需要主管審核
    review_status: str         # pending / approved / rejected
    reviewer_comment: str      # 主管意見
    final_action: str          # 最終處理動作
    error: str                 # 錯誤訊息
    steps: list                # 流程步驟紀錄


# ============================================================
# Prompt 定義
# ============================================================
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "你是工安 AI 分析師。分析以下 YOLO 偵測結果，指出違規情況與風險。"
     "回覆格式：1) 違規摘要 2) 風險評估 3) 建議措施。控制在 100 字內。"),
    ("human", "偵測結果：\n未戴安全帽人數：{no_helmet_count}\n戴安全帽人數：{helmet_count}\n偵測明細：{detections}")
])
analyze_chain = analyze_prompt | llm | parser

alert_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "根據工安分析結果生成告警訊息。"
     "高風險加【緊急】前綴，低風險加【提醒】前綴。"
     "訊息控制在 50 字內，包含違規人數與建議。"),
    ("human", "風險等級：{risk_level}\n分析：{analysis}")
])
alert_chain = alert_prompt | llm | parser


# ============================================================
# Node 函式
# ============================================================
def classify_risk(state: AlertState) -> dict:
    """根據 Rule Engine 規則判斷風險等級"""
    event = state["event"]
    no_helmet = event.get("no_helmet_count", 0)
    total = no_helmet + event.get("helmet_count", 0)

    if no_helmet >= 3 or (total > 0 and no_helmet / max(total, 1) > 0.5):
        risk = "high"
    else:
        risk = "low"

    return {
        "risk_level": risk,
        "steps": state.get("steps", []) + [{
            "node": "classify_risk",
            "result": risk,
            "reason": f"未戴帽 {no_helmet}/{total} 人",
        }],
    }


def llm_analyze(state: AlertState) -> dict:
    """LLM 分析偵測結果"""
    event = state["event"]
    retry = state.get("retry_count", 0)

    try:
        analysis = analyze_chain.invoke({
            "no_helmet_count": event.get("no_helmet_count", 0),
            "helmet_count": event.get("helmet_count", 0),
            "detections": str(event.get("detections", [])),
        })
        return {
            "analysis": analysis,
            "error": "",
            "steps": state.get("steps", []) + [{
                "node": "llm_analyze",
                "result": analysis[:80],
                "retry": retry,
            }],
        }
    except Exception as e:
        return {
            "error": str(e)[:100],
            "retry_count": retry + 1,
            "steps": state.get("steps", []) + [{
                "node": "llm_analyze",
                "result": f"失敗 (retry {retry + 1})",
                "error": str(e)[:60],
            }],
        }


def should_retry(state: AlertState) -> Literal["retry", "generate_alert", "fail"]:
    """判斷是否重試"""
    if not state.get("error"):
        return "generate_alert"
    if state.get("retry_count", 0) < state.get("max_retries", 3):
        return "retry"
    return "fail"


def generate_alert(state: AlertState) -> dict:
    """生成告警訊息"""
    try:
        alert = alert_chain.invoke({
            "risk_level": state["risk_level"],
            "analysis": state.get("analysis", "無分析結果"),
        })
    except Exception:
        alert = f"【{'緊急' if state['risk_level'] == 'high' else '提醒'}】偵測到工安違規，請立即處理。"

    needs_review = state["risk_level"] == "high"

    return {
        "alert_message": alert,
        "needs_review": needs_review,
        "review_status": "pending" if needs_review else "auto_approved",
        "steps": state.get("steps", []) + [{
            "node": "generate_alert",
            "result": alert[:60],
            "needs_review": needs_review,
        }],
    }


def handle_fail(state: AlertState) -> dict:
    """重試耗盡，標記失敗"""
    return {
        "alert_message": "【系統】LLM 分析失敗，已重試 3 次，請人工處理。",
        "needs_review": True,
        "review_status": "pending",
        "final_action": "escalate_to_manual",
        "steps": state.get("steps", []) + [{
            "node": "handle_fail",
            "result": "重試耗盡，轉人工處理",
        }],
    }


def route_by_risk(state: AlertState) -> Literal["high_risk", "low_risk"]:
    """根據風險等級分流"""
    return "high_risk" if state["risk_level"] == "high" else "low_risk"


def high_risk_handler(state: AlertState) -> dict:
    """高風險處理：需要主管審核（HITL）"""
    return {
        "final_action": "await_supervisor_review",
        "steps": state.get("steps", []) + [{
            "node": "high_risk_handler",
            "result": "等待主管審核 (Human-in-the-Loop)",
        }],
    }


def low_risk_handler(state: AlertState) -> dict:
    """低風險處理：自動記錄"""
    return {
        "final_action": "auto_logged",
        "review_status": "auto_approved",
        "steps": state.get("steps", []) + [{
            "node": "low_risk_handler",
            "result": "低風險，自動記錄",
        }],
    }


# ============================================================
# 建構 StateGraph
# ============================================================
def build_workflow() -> StateGraph:
    """建構 LangGraph StateGraph 工作流"""
    builder = StateGraph(AlertState)

    # 加入節點
    builder.add_node("classify_risk", classify_risk)
    builder.add_node("llm_analyze", llm_analyze)
    builder.add_node("generate_alert", generate_alert)
    builder.add_node("handle_fail", handle_fail)
    builder.add_node("high_risk_handler", high_risk_handler)
    builder.add_node("low_risk_handler", low_risk_handler)

    # 設定邊
    builder.add_edge(START, "classify_risk")
    builder.add_edge("classify_risk", "llm_analyze")

    # 重試迴圈（最多 3 次）
    builder.add_conditional_edges("llm_analyze", should_retry, {
        "generate_alert": "generate_alert",
        "retry": "llm_analyze",
        "fail": "handle_fail",
    })

    # 高低風險分流
    builder.add_conditional_edges("generate_alert", route_by_risk, {
        "high_risk": "high_risk_handler",
        "low_risk": "low_risk_handler",
    })

    builder.add_edge("high_risk_handler", END)
    builder.add_edge("low_risk_handler", END)
    builder.add_edge("handle_fail", END)

    return builder.compile()


# 全域 workflow 實例
workflow = build_workflow()


def process_event(event: dict) -> dict:
    """處理單一 YOLO Event"""
    initial_state: AlertState = {
        "event": event,
        "risk_level": "",
        "analysis": "",
        "alert_message": "",
        "retry_count": 0,
        "max_retries": 3,
        "needs_review": False,
        "review_status": "",
        "reviewer_comment": "",
        "final_action": "",
        "error": "",
        "steps": [],
    }
    result = workflow.invoke(initial_state)
    return result


def approve_event(event_result: dict, approved: bool, comment: str = "") -> dict:
    """主管審核（Human-in-the-Loop）"""
    event_result["review_status"] = "approved" if approved else "rejected"
    event_result["reviewer_comment"] = comment
    event_result["final_action"] = "confirmed" if approved else "rejected_needs_action"
    event_result["steps"] = event_result.get("steps", []) + [{
        "node": "supervisor_review",
        "result": "approved" if approved else "rejected",
        "comment": comment,
    }]
    return event_result
