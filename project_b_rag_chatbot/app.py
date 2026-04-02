"""
app.py — FastAPI 後端（RAG 客服 ChatBot API）

啟動方式：
  uvicorn app:app --reload --host 0.0.0.0 --port 8000

API 端點：
  GET  /           → 聊天介面（前端頁面）
  POST /api/chat   → 接收問題，回傳 RAG 回答
  GET  /api/health → 健康檢查
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from rag_engine import RAGEngine

# ========================================
# 建立 FastAPI app
# ========================================
app = FastAPI(
    title="RAG 智慧客服",
    description="基於 RAG + Gemini 的 FAQ 問答系統",
    version="1.0.0",
)

# 靜態檔案（CSS/JS）和模板（HTML）
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 啟動時載入 RAG 引擎（只建一次索引）
print("啟動 RAG 引擎...")
rag = RAGEngine(faq_path="data/faq.txt")
print("RAG 引擎就緒！\n")


# ========================================
# 資料模型
# ========================================
class ChatRequest(BaseModel):
    """使用者傳入的聊天請求"""
    question: str                                      # 使用者問題


class ChatResponse(BaseModel):
    """系統回傳的聊天回覆"""
    answer: str                                        # AI 回答
    sources: list                                      # 引用來源


# ========================================
# API 端點
# ========================================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首頁：聊天介面"""
    return templates.TemplateResponse(request=request, name="chat.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """聊天 API：接收問題 → RAG 搜尋 → Gemini 回答"""
    result = rag.ask(req.question)
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
    )


@app.get("/api/health")
async def health():
    """健康檢查"""
    return {
        "status": "ok",
        "faq_count": len(rag.docs),
    }
