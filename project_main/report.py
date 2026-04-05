"""
report.py -- pandas 事件統計 + LLM 每日摘要報告

職責：
  1. 用 pandas 進行告警事件統計分析（去重、累積、計數）
  2. 由 LLM (Gemini / OpenAI) 生成人類可讀的每日摘要報告
"""

import os
from datetime import datetime
from dotenv import load_dotenv

import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5)
parser = StrOutputParser()

report_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "你是工安報告撰寫員。根據以下統計數據，撰寫一份簡潔的每日工安摘要報告。"
     "報告應包含：1) 總覽 2) 重點違規 3) 趨勢觀察 4) 建議改善措施。"
     "語氣專業、簡潔，控制在 300 字內。使用繁體中文。"),
    ("human", "日期：{date}\n統計數據：\n{stats}")
])
report_chain = report_prompt | llm | parser


class ReportGenerator:
    """事件統計 + 每日摘要報告"""

    def __init__(self):
        self.events: list[dict] = []

    def add_event(self, event: dict, workflow_result: dict):
        """記錄一筆處理完成的事件"""
        self.events.append({
            "timestamp": event.get("timestamp", datetime.now().isoformat()),
            "helmet_count": event.get("helmet_count", 0),
            "no_helmet_count": event.get("no_helmet_count", 0),
            "risk_level": workflow_result.get("risk_level", "unknown"),
            "review_status": workflow_result.get("review_status", ""),
            "alert_message": workflow_result.get("alert_message", ""),
            "demo_mode": event.get("demo_mode", False),
        })

    def get_stats(self) -> dict:
        """用 pandas 計算統計數據"""
        if not self.events:
            return {
                "total_events": 0,
                "total_violations": 0,
                "high_risk_count": 0,
                "low_risk_count": 0,
                "avg_violations_per_event": 0,
                "review_pending": 0,
                "review_approved": 0,
                "review_rejected": 0,
            }

        df = pd.DataFrame(self.events)

        stats = {
            "total_events": len(df),
            "total_violations": int(df["no_helmet_count"].sum()),
            "total_compliant": int(df["helmet_count"].sum()),
            "high_risk_count": int((df["risk_level"] == "high").sum()),
            "low_risk_count": int((df["risk_level"] == "low").sum()),
            "avg_violations_per_event": round(float(df["no_helmet_count"].mean()), 2),
            "max_violations_single": int(df["no_helmet_count"].max()),
            "review_pending": int((df["review_status"] == "pending").sum()),
            "review_approved": int((df["review_status"].isin(["approved", "auto_approved"])).sum()),
            "review_rejected": int((df["review_status"] == "rejected").sum()),
        }

        return stats

    def generate_daily_report(self) -> dict:
        """生成 LLM 每日摘要報告"""
        stats = self.get_stats()
        today = datetime.now().strftime("%Y-%m-%d")

        if stats["total_events"] == 0:
            return {
                "date": today,
                "stats": stats,
                "report": "今日無工安偵測事件記錄。",
            }

        try:
            report_text = report_chain.invoke({
                "date": today,
                "stats": str(stats),
            })
        except Exception as e:
            report_text = (
                f"【自動摘要】{today}\n"
                f"共處理 {stats['total_events']} 件偵測事件，"
                f"發現 {stats['total_violations']} 人次違規，"
                f"其中高風險 {stats['high_risk_count']} 件。"
                f"（LLM 摘要生成失敗：{str(e)[:50]}）"
            )

        return {
            "date": today,
            "stats": stats,
            "report": report_text,
        }

    def get_events_df(self) -> pd.DataFrame:
        """取得事件 DataFrame（供進階分析）"""
        if not self.events:
            return pd.DataFrame()
        return pd.DataFrame(self.events)
