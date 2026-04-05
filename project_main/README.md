# 工安影像辨識 AI 告警系統

工地安全管理仰賴人工抽查，事故後才能補救。本系統以 YOLOv8 訓練安全帽偵測模型，導入 KMeans 自動校準信心度門檻取代人工設定，以 LangGraph StateGraph 實作高低風險分流、3 次重試迴圈與 Human-in-the-Loop 主管審核，最終由 LLM 生成每日摘要報告。從影像輸入到人類可讀報告，全程自動化。

## 架構

```
影像輸入
   │
   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────────────┐
│  YOLOv8     │────▶│  KMeans      │────▶│  LangGraph StateGraph   │
│  Inference  │     │  校準門檻    │     │                         │
│             │     │              │     │  classify_risk           │
│  安全帽偵測  │     │  自動取代    │     │      │                  │
│  Event JSON │     │  人工設定    │     │      ▼                  │
└─────────────┘     └──────────────┘     │  llm_analyze ←─ 重試x3  │
                                         │      │                  │
                                         │      ▼                  │
                                         │  generate_alert         │
                                         │      │                  │
                                         │   ┌──┴──┐               │
                                         │   ▼     ▼               │
                                         │  高風險  低風險          │
                                         │  HITL   自動記錄        │
                                         │  主管審核               │
                                         └─────────────────────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │  pandas 統計分析     │
                                         │  LLM 每日摘要報告   │
                                         └─────────────────────┘
```

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | Dashboard 首頁 |
| POST | `/detect` | 上傳影像 → YOLO 偵測 → Workflow |
| GET | `/events` | 查詢所有事件 (JSON) |
| GET | `/recalibrate` | KMeans 門檻重新校準 |
| POST | `/review/{id}` | 主管審核 (HITL) |
| GET | `/report` | LLM 每日摘要報告 |

## 技術棧

| 技術 | 用途 |
|------|------|
| YOLOv8 | 安全帽偵測模型推論 |
| scikit-learn KMeans | 信心度門檻自動校準 |
| LangGraph StateGraph | 工作流編排（分流、重試、HITL） |
| LangChain | LLM Prompt 管理 |
| Gemini API | AI 分析與報告生成 |
| FastAPI | REST API Server |
| pandas | 事件統計分析 |
| Rule Engine | rules.yaml 規則比對 |

## 快速啟動

```bash
cd project_main
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env 填入 GOOGLE_API_KEY
uvicorn app:app --reload --host 0.0.0.0 --port 8003
# 開啟 http://127.0.0.1:8003
```
