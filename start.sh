#!/bin/bash
# 一鍵啟動全部服務

# 專案根目錄（自動偵測 script 所在位置）
DIR="$(cd "$(dirname "$0")" && pwd)"

echo "啟動 AI 工安解決方案..."
echo "根目錄: $DIR"
echo ""

# 殺掉舊的程序
kill $(lsof -t -i:8000) 2>/dev/null
kill $(lsof -t -i:8001) 2>/dev/null
kill $(lsof -t -i:8002) 2>/dev/null
kill $(lsof -t -i:8003) 2>/dev/null
kill $(lsof -t -i:8080) 2>/dev/null

# 啟動各專案（背景執行）
cd "$DIR/project_b_rag_chatbot"
uvicorn app:app --host 0.0.0.0 --port 8000 &

cd "$DIR/project_a_safety_monitor"
uvicorn app:app --host 0.0.0.0 --port 8001 &

cd "$DIR/project_c_llm_orchestration"
uvicorn app:app --host 0.0.0.0 --port 8002 &

cd "$DIR/project_main"
uvicorn app:app --host 0.0.0.0 --port 8003 &

# 啟動入口頁面
cd "$DIR"
uvicorn app:app --host 0.0.0.0 --port 8080 &

sleep 5
echo ""
echo "全部啟動完成！"
echo ""
echo "  入口頁面:  http://127.0.0.1:8080"
echo "  工安監控:  http://127.0.0.1:8001"
echo "  RAG 客服:  http://127.0.0.1:8000"
echo "  LLM 編排:  http://127.0.0.1:8002"
echo "  核心專案:  http://127.0.0.1:8003"
echo ""
