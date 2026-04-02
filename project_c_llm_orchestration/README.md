# LLM 多步驟編排系統

用 LangChain 串接 5 步 AI 流程，自動處理工安違規事件。

## 功能

- 輸入違規事件 → AI 自動執行 5 步流程
- Step 1: 分析嚴重程度（高/中/低）
- Step 2: 分類違規類型
- Step 3: 查詢對應法規
- Step 4: 生成告警訊息
- Step 5: 判斷是否通知主管
- 累積狀態追蹤（歷史紀錄 + 統計）

## 架構

```
違規事件 → Chain 1(分析) → Chain 2(分類) → 查法規 → Chain 3(告警) → Chain 4(通知判斷)
                                                                            ↓
                                                                    累積到 SafetyState
```

## 啟動

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --host 0.0.0.0 --port 8002
# http://127.0.0.1:8002
```

## 技術棧

- **LangChain**: LCEL Chain 組合（prompt | llm | parser）
- **Gemini**: 作為 LLM 後端
- **FastAPI**: Web 後端
- **SafetyState**: 累積狀態管理
