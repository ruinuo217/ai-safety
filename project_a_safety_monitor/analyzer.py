"""
analyzer.py — 工安監控 AI 分析引擎

職責：接收工地照片 → Gemini 分析違規 → 回傳結構化 JSON
"""

import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# 法規資料庫
REGULATIONS = {
    "no_helmet": "職安法第 281 條：雇主應使勞工確實使用安全帽。罰鍰 3~30 萬元。",
    "no_vest": "職安法第 277 條：有車輛通行區域應穿著反光背心。罰鍰 3~15 萬元。",
    "no_belt": "職安法第 225 條：2 公尺以上作業應使用安全帶。罰鍰 3~30 萬元。",
    "blocked_exit": "建築技術規則第 97 條：緊急出口應保持暢通。",
    "exposed_wire": "職安法第 246 條：臨時用電應加保護套管。",
    "other": "請查閱職業安全衛生法相關條文。",
}


class SafetyAnalyzer:
    """工安分析器：圖片 → Gemini 分析 → JSON 報告"""

    def __init__(self):
        # 用 response_mime_type 保證輸出 JSON
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"},
        )
        # 普通文字模型（用於生成告警訊息）
        self.text_model = genai.GenerativeModel("gemini-2.5-flash")

    def analyze_image(self, image_path: str) -> dict:
        """分析工地照片，回傳結構化報告"""
        image = Image.open(image_path)

        prompt = """分析這張工地監控照片，輸出 JSON：
{
    "person_count": 人數,
    "violations": [
        {
            "person_id": 編號,
            "type": "no_helmet/no_vest/no_belt/blocked_exit/exposed_wire/other",
            "severity": "high/medium/low",
            "location": "位置描述"
        }
    ],
    "safety_score": 0到100的安全評分,
    "scene_description": "場景簡述"
}"""

        response = self.model.generate_content([prompt, image])
        analysis = json.loads(response.text)

        # 補上法規依據
        for v in analysis.get("violations", []):
            v["regulation"] = REGULATIONS.get(v.get("type", "other"), REGULATIONS["other"])

        return analysis

    def analyze_text(self, description: str) -> dict:
        """用文字描述分析（沒有圖片時）"""
        prompt = f"""分析以下工安事件描述，輸出 JSON：
事件：{description}

{{
    "person_count": 人數,
    "violations": [
        {{
            "person_id": 編號,
            "type": "no_helmet/no_vest/no_belt/blocked_exit/exposed_wire/other",
            "severity": "high/medium/low",
            "location": "位置描述"
        }}
    ],
    "safety_score": 0到100,
    "scene_description": "場景簡述"
}}"""

        response = self.model.generate_content(prompt)
        analysis = json.loads(response.text)

        for v in analysis.get("violations", []):
            v["regulation"] = REGULATIONS.get(v.get("type", "other"), REGULATIONS["other"])

        return analysis

    def generate_alert(self, analysis: dict) -> str:
        """根據分析結果生成告警訊息"""
        violations = analysis.get("violations", [])
        if not violations:
            return "未發現違規，現場安全狀況良好。"

        high_count = sum(1 for v in violations if v.get("severity") == "high")
        prompt = f"""根據以下工安分析結果，生成一段簡短的告警訊息（50字內）：
安全評分：{analysis.get('safety_score', '?')}/100
違規數：{len(violations)} 項（嚴重 {high_count} 項）
違規類型：{', '.join(v.get('type','') for v in violations)}
"""
        response = self.text_model.generate_content(prompt)
        return response.text.strip()
