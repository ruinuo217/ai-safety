"""
app.py -- 工安影像辨識 AI 告警系統（FastAPI REST Server）

端點：
  GET   /              → Dashboard 首頁
  POST  /detect        → 上傳影像 → YOLO 偵測 → Workflow 處理
  GET   /events        → 查詢所有事件
  GET   /recalibrate   → 觸發 KMeans 門檻重新校準
  POST  /review/{id}   → 主管審核（Human-in-the-Loop）
  GET   /report        → 每日摘要報告
  GET   /api/health    → 健康檢查

啟動方式：
  uvicorn app:app --reload --host 0.0.0.0 --port 8003
"""

import os
import uuid
from datetime import datetime

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from yolo_detector import YOLODetector
from threshold import ThresholdCalibrator
from workflow import process_event, approve_event
from rule_engine import evaluate_event, get_highest_severity
from report import ReportGenerator

# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="工安影像辨識 AI 告警系統",
    description="YOLOv8 偵測 → KMeans 校準 → LangGraph Workflow → LLM 報告",
    version="1.0.0",
)

os.makedirs("data/uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# ============================================================
# 初始化各元件
# ============================================================
print("=" * 50)
print("工安影像辨識 AI 告警系統 啟動中...")
print("=" * 50)

detector = YOLODetector()
calibrator = ThresholdCalibrator()
reporter = ReportGenerator()

# 事件存儲（正式環境會用資料庫）
event_store: list[dict] = []

print("系統就緒！")
print(f"YOLO Demo Mode: {detector.demo_mode}")
print(f"初始信心度門檻: {calibrator.get_threshold()}")
print("=" * 50 + "\n")


# ============================================================
# Dashboard 首頁
# ============================================================
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = reporter.get_stats()
    threshold_stats = calibrator.get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": event_store[:20],
            "stats": stats,
            "threshold": threshold_stats,
            "demo_mode": detector.demo_mode,
        },
    )


# ============================================================
# POST /detect -- 偵測影像
# ============================================================
@app.post("/detect")
async def detect(request: Request, file: UploadFile = File(None)):
    """上傳影像 → YOLO 偵測 → Rule Engine → LangGraph Workflow"""

    # 1. 儲存上傳圖片（或使用 demo 圖片）
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4().hex[:8]}.{ext}"
        filepath = f"data/uploads/{filename}"
        with open(filepath, "wb") as f:
            content = await file.read()
            f.write(content)
        image_url = f"/uploads/{filename}"
    else:
        filepath = "data/sample.jpg"
        image_url = None

    # 2. YOLO 偵測
    threshold = calibrator.get_threshold()
    yolo_result = detector.detect(filepath, conf_threshold=threshold)

    # 3. 收集信心度供 KMeans 校準
    for d in yolo_result.get("detections", []):
        calibrator.add_confidences([d["confidence"]])

    # 4. Rule Engine 評估
    triggered_rules = evaluate_event(yolo_result)
    severity = get_highest_severity(triggered_rules)

    # 5. LangGraph Workflow 處理
    workflow_result = process_event(yolo_result)

    # 6. 記錄事件
    event_id = f"EVT-{len(event_store)+1:04d}"
    record = {
        "id": event_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_url": image_url,
        "yolo_result": yolo_result,
        "triggered_rules": triggered_rules,
        "rule_severity": severity,
        "workflow": {
            "risk_level": workflow_result.get("risk_level", ""),
            "analysis": workflow_result.get("analysis", ""),
            "alert_message": workflow_result.get("alert_message", ""),
            "review_status": workflow_result.get("review_status", ""),
            "final_action": workflow_result.get("final_action", ""),
            "steps": workflow_result.get("steps", []),
        },
    }
    event_store.insert(0, record)
    reporter.add_event(yolo_result, workflow_result)

    # 回傳 Dashboard
    stats = reporter.get_stats()
    threshold_stats = calibrator.get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": event_store[:20],
            "stats": stats,
            "threshold": threshold_stats,
            "result": record,
            "demo_mode": detector.demo_mode,
        },
    )


# ============================================================
# GET /events -- 查詢事件
# ============================================================
@app.get("/events")
async def get_events():
    return {"events": event_store, "total": len(event_store)}


# ============================================================
# GET /recalibrate -- KMeans 門檻重新校準
# ============================================================
@app.get("/recalibrate")
async def recalibrate(request: Request):
    result = calibrator.calibrate()
    stats = reporter.get_stats()
    threshold_stats = calibrator.get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": event_store[:20],
            "stats": stats,
            "threshold": threshold_stats,
            "calibration": result,
            "demo_mode": detector.demo_mode,
        },
    )


# ============================================================
# POST /review/{event_id} -- 主管審核（HITL）
# ============================================================
@app.post("/review/{event_id}")
async def review(request: Request, event_id: str, action: str = Form(...), comment: str = Form("")):
    """主管審核：approve / reject"""
    record = next((e for e in event_store if e["id"] == event_id), None)
    if not record:
        return {"error": "Event not found"}

    approved = action == "approve"
    record["workflow"]["review_status"] = "approved" if approved else "rejected"
    record["workflow"]["reviewer_comment"] = comment
    record["workflow"]["final_action"] = "confirmed" if approved else "rejected_needs_action"
    record["workflow"]["steps"].append({
        "node": "supervisor_review",
        "result": "approved" if approved else "rejected",
        "comment": comment,
    })

    stats = reporter.get_stats()
    threshold_stats = calibrator.get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": event_store[:20],
            "stats": stats,
            "threshold": threshold_stats,
            "review_done": {"event_id": event_id, "action": action},
            "demo_mode": detector.demo_mode,
        },
    )


# ============================================================
# GET /report -- 每日摘要報告
# ============================================================
@app.get("/report")
async def daily_report(request: Request):
    report = reporter.generate_daily_report()
    stats = reporter.get_stats()
    threshold_stats = calibrator.get_stats()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "events": event_store[:20],
            "stats": stats,
            "threshold": threshold_stats,
            "report": report,
            "demo_mode": detector.demo_mode,
        },
    )


# ============================================================
# GET /api/health
# ============================================================
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "demo_mode": detector.demo_mode,
        "threshold": calibrator.get_threshold(),
        "total_events": len(event_store),
    }
