"""
app.py — AI 工安監控系統（FastAPI 後端）

功能：
  上傳工地照片 → Gemini AI 分析違規 → 結構化報告 + 告警

啟動方式：
  uvicorn app:app --reload --host 0.0.0.0 --port 8001
"""

import os
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from analyzer import SafetyAnalyzer

app = FastAPI(
    title="AI 工安監控系統",
    description="上傳工地照片 → AI 自動偵測違規 → 結構化報告",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# 初始化分析器
print("初始化 AI 分析引擎...")
analyzer = SafetyAnalyzer()
print("AI 分析引擎就緒！\n")

# 歷史紀錄（正式系統會用資料庫）
history = []


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"history": history})


@app.post("/analyze")
async def analyze(request: Request, file: UploadFile = File(None), text_input: str = Form(None)):
    """分析上傳的照片或文字描述"""
    result = {}
    image_url = None

    try:
        if file and file.filename:
            # 儲存上傳的圖片
            ext = file.filename.split(".")[-1]
            filename = f"{uuid.uuid4().hex[:8]}.{ext}"
            filepath = f"data/uploads/{filename}"
            with open(filepath, "wb") as f:
                content = await file.read()
                f.write(content)
            image_url = f"/uploads/{filename}"

            # AI 分析圖片
            analysis = analyzer.analyze_image(filepath)
        elif text_input and text_input.strip():
            # AI 分析文字描述
            analysis = analyzer.analyze_text(text_input.strip())
        else:
            return templates.TemplateResponse(
                request=request, name="index.html",
                context={"history": history, "error": "請上傳照片或輸入文字描述"}
            )

        # 生成告警訊息
        alert = analyzer.generate_alert(analysis)

        # 組合結果
        result = {
            "id": f"RPT-{len(history)+1:04d}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_url": image_url,
            "analysis": analysis,
            "alert": alert,
        }

        # 存入歷史
        history.insert(0, result)

    except Exception as e:
        return templates.TemplateResponse(
            request=request, name="index.html",
            context={"history": history, "error": f"分析失敗：{str(e)[:100]}"}
        )

    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"history": history, "result": result}
    )


@app.get("/api/history")
async def get_history():
    return {"reports": history}
