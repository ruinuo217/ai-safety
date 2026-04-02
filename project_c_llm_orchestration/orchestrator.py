"""
orchestrator.py — LLM 多步驟編排引擎

職責：
  接收違規事件 → 自動執行多步驟流程：
  分析嚴重程度 → 查法規 → 生成告警 → 判斷是否通知主管 → 記錄事件
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
parser = StrOutputParser()

# ========================================
# 法規資料庫
# ========================================
REGULATIONS = {
    "no_helmet": "職安法第 281 條：雇主應使勞工確實使用安全帽。罰鍰 3~30 萬元。",
    "no_vest": "職安法第 277 條：有車輛通行區域應穿著反光背心。罰鍰 3~15 萬元。",
    "no_belt": "職安法第 225 條：2 公尺以上作業應使用安全帶。罰鍰 3~30 萬元。",
    "blocked_exit": "建築技術規則第 97 條：緊急出口應保持暢通。",
    "noise": "職安法第 300 條：噪音超標應提供聽力防護。",
    "chemical": "危化標示規則第 5 條：危險化學品應張貼標示。",
}

# ========================================
# 累積狀態（記錄所有處理過的事件）
# ========================================
class SafetyState:
    def __init__(self):
        self.events = []
        self.alert_count = 0

    def add_event(self, event: dict):
        self.events.append(event)
        if event.get("severity") == "高":
            self.alert_count += 1

    def get_stats(self):
        total = len(self.events)
        high = sum(1 for e in self.events if e.get("severity") == "高")
        return {"total": total, "high": high, "alert_count": self.alert_count}


state = SafetyState()

# ========================================
# Chain 1：分析嚴重程度
# ========================================
analyze_prompt = ChatPromptTemplate.from_messages([
    ("system", "分析違規事件的嚴重程度，只回答一個字：低、中、高。不要解釋。"),
    ("human", "違規事件：{violation}")
])
analyze_chain = analyze_prompt | llm | parser

# ========================================
# Chain 2：分類違規類型
# ========================================
classify_prompt = ChatPromptTemplate.from_messages([
    ("system", "判斷違規類型，只回答一個代碼：no_helmet/no_vest/no_belt/blocked_exit/noise/chemical/other。不要解釋。"),
    ("human", "違規事件：{violation}")
])
classify_chain = classify_prompt | llm | parser

# ========================================
# Chain 3：生成告警訊息
# ========================================
alert_prompt = ChatPromptTemplate.from_messages([
    ("system", "根據違規資訊生成一句簡短告警訊息（30字內）。"
               "高→加【緊急】，中→加【注意】，低→加【提醒】。"),
    ("human", "違規：{violation}\n嚴重程度：{severity}\n法規：{regulation}")
])
alert_chain = alert_prompt | llm | parser

# ========================================
# Chain 4：判斷是否通知主管
# ========================================
notify_prompt = ChatPromptTemplate.from_messages([
    ("system", "判斷是否需要通知主管，只回答：是 或 否。\n"
               "規則：嚴重程度「高」→是，累積3件以上→是，其他→否。"),
    ("human", "嚴重程度：{severity}\n目前累積違規：{total_events} 件")
])
notify_chain = notify_prompt | llm | parser


def process_violation(violation: str) -> dict:
    """完整編排流程：分析 → 分類 → 查法規 → 告警 → 判斷通知 → 記錄"""
    steps = []

    # Step 1：分析嚴重程度
    severity = analyze_chain.invoke({"violation": violation}).strip()
    steps.append({"step": 1, "name": "分析嚴重程度", "result": severity})

    # Step 2：分類違規類型
    vtype = classify_chain.invoke({"violation": violation}).strip()
    steps.append({"step": 2, "name": "分類違規類型", "result": vtype})

    # Step 3：查法規（本地查詢，不需要 LLM）
    regulation = REGULATIONS.get(vtype, "請查閱職業安全衛生法相關條文。")
    steps.append({"step": 3, "name": "查詢法規", "result": regulation})

    # Step 4：生成告警訊息
    alert = alert_chain.invoke({
        "violation": violation,
        "severity": severity,
        "regulation": regulation,
    }).strip()
    steps.append({"step": 4, "name": "生成告警", "result": alert})

    # Step 5：判斷是否通知主管
    stats = state.get_stats()
    should_notify = notify_chain.invoke({
        "severity": severity,
        "total_events": str(stats["total"]),
    }).strip()
    steps.append({"step": 5, "name": "判斷通知主管", "result": should_notify})

    # 記錄事件
    event = {
        "violation": violation,
        "severity": severity,
        "type": vtype,
        "regulation": regulation,
        "alert": alert,
        "notify": should_notify,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    state.add_event(event)

    return {
        "event": event,
        "steps": steps,
        "stats": state.get_stats(),
    }
