# AI 工安監控系統

上傳工地照片 → Gemini AI 自動偵測違規 → 結構化報告 + 告警通知

## 功能

- 上傳監控照片或輸入文字描述
- AI 自動偵測：未戴安全帽、未穿反光背心、未繫安全帶等
- 結構化 JSON 報告（安全評分、違規清單、法規依據）
- 自動生成告警訊息
- 歷史紀錄查看

## 架構

```
工地照片 → Gemini 多模態分析 → JSON Schema 強制輸出 → 比對法規 → 生成告警
```

## 啟動方式

```bash
pip install -r requirements.txt
cp .env.example .env  # 填入 GOOGLE_API_KEY
uvicorn app:app --reload --host 0.0.0.0 --port 8001
# 開啟 http://127.0.0.1:8001
```

## 技術棧

- **AI**: Gemini 2.5 Flash（多模態圖片分析）
- **結構化輸出**: response_mime_type="application/json"
- **後端**: FastAPI
- **前端**: Jinja2 + 原生 CSS
