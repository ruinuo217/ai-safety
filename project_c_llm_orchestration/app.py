"""
app.py — LLM 多步驟編排系統（FastAPI 後端）

功能：
  輸入違規事件 → AI 自動跑 5 步流程 → 即時顯示每步結果

啟動方式：
  uvicorn app:app --reload --host 0.0.0.0 --port 8002
"""

import os
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from orchestrator import process_violation, state

app = FastAPI(
    title="LLM 多步驟編排系統",
    description="違規事件 → 5 步 AI 自動處理流程",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"history": state.events[::-1], "stats": state.get_stats()}
    )


@app.post("/process")
async def process(request: Request, violation: str = Form(...)):
    result = None
    error = None

    try:
        result = process_violation(violation)
    except Exception as e:
        error = str(e)[:150]

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={
            "result": result,
            "error": error,
            "history": state.events[::-1],
            "stats": state.get_stats(),
        }
    )
