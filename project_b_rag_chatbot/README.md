# RAG 智慧客服 ChatBot

基於 RAG（Retrieval-Augmented Generation）+ Gemini + FastAPI 的智慧客服系統。

## 功能

- 上傳 FAQ / 產品手冊 → 自動建立向量索引
- 客戶提問 → 語意搜尋最相關的 FAQ → Gemini 生成回答
- Web 聊天介面，可嵌入官網
- 顯示引用來源和相似度分數

## 架構

```
客戶提問 → Embedding → 向量搜尋（cosine similarity）→ 取 top 3 → Gemini 生成回答
```

## 啟動方式

```bash
# 1. 安裝套件
pip install -r requirements.txt

# 2. 設定 API Key
cp .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY

# 3. 啟動服務
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 4. 開啟瀏覽器
# http://localhost:8000
```

## 技術棧

- **LLM**: Google Gemini 2.5 Flash
- **Embedding**: Gemini Embedding API
- **後端**: FastAPI
- **前端**: 原生 HTML/CSS/JS
- **向量搜尋**: scikit-learn cosine similarity

## API

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 聊天介面 |
| `/api/chat` | POST | `{"question": "退貨政策？"}` → `{"answer": "...", "sources": [...]}` |
| `/api/health` | GET | 健康檢查 |

## 商業化方向

- 接客戶的 FAQ / 產品手冊 / 內部文件
- 嵌入官網或 LINE 做 ChatBot
- SaaS 月租模式
