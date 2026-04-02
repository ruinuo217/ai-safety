"""
AI 工安解決方案 — Portfolio 首頁

一個入口，三個專案 Demo
啟動方式：
  cd ~/portfolio
  uvicorn app:app --reload --host 0.0.0.0 --port 8080
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI(title="AI 工安解決方案")

HTML = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 工安解決方案</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", sans-serif;
    background: #0f172a;
    color: white;
    min-height: 100vh;
}
.hero {
    text-align: center;
    padding: 60px 20px 40px;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}
.hero h1 {
    font-size: 36px;
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
}
.hero p { color: #94a3b8; font-size: 16px; max-width: 600px; margin: 0 auto; line-height: 1.8; }
.tech-tags { margin-top: 20px; display: flex; gap: 8px; justify-content: center; flex-wrap: wrap; }
.tech-tag {
    padding: 4px 12px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    font-size: 12px;
    color: #94a3b8;
}
.cards { max-width: 960px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
.card {
    background: #1e293b;
    border-radius: 16px;
    padding: 28px;
    border: 1px solid #334155;
    transition: all 0.3s;
    cursor: pointer;
    text-decoration: none;
    color: white;
    display: block;
}
.card:hover {
    transform: translateY(-4px);
    border-color: #60a5fa;
    box-shadow: 0 8px 30px rgba(96,165,250,0.15);
}
.card .icon { font-size: 36px; margin-bottom: 14px; }
.card h2 { font-size: 20px; margin-bottom: 8px; }
.card .desc { font-size: 14px; color: #94a3b8; line-height: 1.7; margin-bottom: 16px; }
.card .stack {
    display: flex; gap: 6px; flex-wrap: wrap;
}
.card .stack span {
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 500;
}
.card.red .stack span { background: rgba(239,68,68,0.15); color: #fca5a5; }
.card.blue .stack span { background: rgba(59,130,246,0.15); color: #93c5fd; }
.card.purple .stack span { background: rgba(139,92,246,0.15); color: #c4b5fd; }
.card .status {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid #334155;
    font-size: 12px;
    color: #64748b;
}
.card .status .dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 4px;
}
.footer {
    text-align: center;
    padding: 40px 20px;
    color: #475569;
    font-size: 13px;
}
.footer a { color: #60a5fa; text-decoration: none; }
</style>
</head>
<body>

<div class="hero">
    <h1>AI 工安解決方案</h1>
    <p>
        運用 Gemini 多模態 AI、RAG 檢索增強生成、LangChain 多步驟編排，
        打造智慧化工安監控系統。從圖片偵測到自動告警，一站式解決。
    </p>
    <div class="tech-tags">
        <span class="tech-tag">Gemini AI</span>
        <span class="tech-tag">RAG</span>
        <span class="tech-tag">LangChain</span>
        <span class="tech-tag">FastAPI</span>
        <span class="tech-tag">Function Calling</span>
        <span class="tech-tag">Embedding</span>
        <span class="tech-tag">Structured Output</span>
    </div>
</div>

<div class="cards">
    <a class="card red" href="http://127.0.0.1:8001" target="_blank">
        <div class="icon">📷</div>
        <h2>AI 工安監控</h2>
        <div class="desc">
            上傳工地照片 → Gemini 多模態 AI 自動偵測違規 →
            結構化 JSON 報告 + 法規依據 + 告警訊息
        </div>
        <div class="stack">
            <span>Gemini Vision</span>
            <span>JSON Schema</span>
            <span>Pillow</span>
        </div>
        <div class="status"><span class="dot"></span>Port 8001</div>
    </a>

    <a class="card blue" href="http://127.0.0.1:8000" target="_blank">
        <div class="icon">💬</div>
        <h2>RAG 智慧客服</h2>
        <div class="desc">
            上傳 FAQ 文件 → Embedding 向量索引 → 語意搜尋 →
            Gemini 生成精準回答，附引用來源
        </div>
        <div class="stack">
            <span>RAG</span>
            <span>Embedding</span>
            <span>Cosine Similarity</span>
        </div>
        <div class="status"><span class="dot"></span>Port 8000</div>
    </a>

    <a class="card purple" href="http://127.0.0.1:8002" target="_blank">
        <div class="icon">⚡</div>
        <h2>LLM 多步驟編排</h2>
        <div class="desc">
            違規事件 → LangChain 自動執行 5 步 AI 流程：
            分析 → 分類 → 查法規 → 告警 → 通知判斷
        </div>
        <div class="stack">
            <span>LangChain</span>
            <span>LCEL Chain</span>
            <span>SafetyState</span>
        </div>
        <div class="status"><span class="dot"></span>Port 8002</div>
    </a>
</div>

<div class="footer">
    Built by Reyna · <a href="https://github.com/reyna" target="_blank">GitHub</a>
</div>

</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML
