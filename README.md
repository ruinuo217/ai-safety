# AI 工安解決方案

運用 Gemini 多模態 AI、RAG 檢索增強生成、LangChain 多步驟編排，打造智慧化工安監控系統。

## Demo

| 專案 | 說明 | 技術 |
|------|------|------|
| **AI 工安監控** | 上傳工地照片 → AI 偵測違規 → 結構化報告 | Gemini Vision, JSON Schema |
| **RAG 智慧客服** | FAQ 問答 ChatBot → 語意搜尋 → AI 回答 | RAG, Embedding, Cosine Similarity |
| **LLM 多步驟編排** | 違規事件 → 5 步 AI 自動處理流程 | LangChain, LCEL, SafetyState |

## 快速啟動

```bash
# 1. 安裝
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 編輯 .env 填入 GOOGLE_API_KEY

# 3. 一鍵啟動全部
bash start.sh

# 4. 開啟入口頁面
# http://127.0.0.1:8080
```

## 架構

```
                    ┌─────────────────┐
                    │   入口首頁:8080  │
                    └────────┬────────┘
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      ┌──────────────┐ ┌──────────┐ ┌──────────────┐
      │ AI 工安:8001 │ │RAG:8000  │ │LLM 編排:8002 │
      │ Gemini Vision│ │Embedding │ │ LangChain    │
      │ JSON Schema  │ │搜尋+生成 │ │ 5步 Chain    │
      └──────────────┘ └──────────┘ └──────────────┘
```

## 技術棧

- **AI**: Google Gemini 2.5 Flash
- **RAG**: Gemini Embedding + Cosine Similarity
- **編排**: LangChain LCEL
- **後端**: FastAPI
- **前端**: Jinja2 + 原生 CSS
