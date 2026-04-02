"""
rag_engine.py — RAG 核心引擎（被 FastAPI 呼叫）

職責：讀取文件 → Embedding → 搜尋 → 生成回答
這個檔案不處理 HTTP，只負責 RAG 邏輯
"""

import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class RAGEngine:
    """RAG 引擎：讀取文件 → 建立索引 → 搜尋 → 回答"""

    def __init__(self, faq_path: str = "data/faq.txt"):
        self.docs = []                                 # 所有 FAQ 段落
        self.embeddings = []                           # 每段的向量
        self._load_docs(faq_path)                      # 讀取文件
        self._build_index()                            # 建立向量索引

    def _load_docs(self, path: str):
        """讀取 FAQ 文件，用空行切段"""
        with open(path, "r", encoding="utf-8") as f:
            chunks = f.read().strip().split("\n\n")
            for chunk in chunks:
                self.docs.append(chunk.strip())
        print(f"[RAG] 載入 {len(self.docs)} 段 FAQ")

    def _embed(self, text: str) -> np.ndarray:
        """文字轉向量"""
        res = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
        )
        return np.array(res.embeddings[0].values)

    def _build_index(self):
        """對所有段落建立向量索引（啟動時只跑一次）"""
        print("[RAG] 建立向量索引中...")
        self.embeddings = [self._embed(doc) for doc in self.docs]
        print(f"[RAG] 索引完成！{len(self.embeddings)} 段，維度 {self.embeddings[0].shape}")

    def search(self, query: str, top_k: int = 3) -> list:
        """向量搜尋，回傳最相關的段落 + 分數"""
        q_emb = self._embed(query)
        sims = cosine_similarity([q_emb], self.embeddings)[0]
        sorted_idx = np.argsort(sims)[::-1][:top_k]

        results = []
        for i in sorted_idx:
            results.append({
                "content": self.docs[i],
                "score": round(float(sims[i]), 3),
            })
        return results

    def ask(self, question: str) -> dict:
        """完整 RAG 流程：搜尋 → 組合 prompt → Gemini 回答"""
        # 搜尋相關段落
        results = self.search(question, top_k=3)

        # 組合 context
        context = "\n\n".join(
            f"[來源 {i+1}（相似度 {r['score']}）]\n{r['content']}"
            for i, r in enumerate(results)
        )

        # 組合 prompt
        prompt = f"""你是一個專業客服助理。請根據以下 FAQ 內容回答客戶的問題。

規則：
- 只根據 FAQ 內容回答，不要編造
- 用繁體中文、親切有禮的語氣
- 如果 FAQ 裡沒有相關資訊，請說「這個問題我需要轉接真人客服為您處理」
- 回答簡潔，不超過 150 字

=== FAQ 內容 ===
{context}

=== 客戶問題 ===
{question}
"""

        # 呼叫 Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"temperature": 0.2},
        )

        return {
            "answer": response.text,
            "sources": results,
        }
