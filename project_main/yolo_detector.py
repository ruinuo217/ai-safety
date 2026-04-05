"""
yolo_detector.py -- YOLOv8 安全帽偵測推論引擎

職責：
  載入 YOLOv8 模型 → 推論工地影像 → 回傳 Event JSON
  支援兩種模式：
    1. 正式模式：使用 ultralytics YOLOv8 模型推論
    2. Demo 模式：無模型時以模擬資料展示完整流程
"""

import os
import json
import random
from datetime import datetime
from typing import Optional

# ============================================================
# 嘗試載入 ultralytics；若未安裝則進入 Demo 模式
# ============================================================
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

# 預設模型路徑（可替換為自行訓練的 best.pt）
DEFAULT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best.pt")


class YOLODetector:
    """YOLOv8 安全帽偵測器"""

    CLASS_NAMES = {0: "Helmet", 1: "No Helmet"}

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model = None
        self.demo_mode = True

        if ULTRALYTICS_AVAILABLE and os.path.exists(model_path):
            try:
                self.model = YOLO(model_path)
                self.demo_mode = False
                print(f"[YOLOv8] 模型已載入: {model_path}")
            except Exception as e:
                print(f"[YOLOv8] 模型載入失敗，進入 Demo 模式: {e}")
        else:
            reason = "ultralytics 未安裝" if not ULTRALYTICS_AVAILABLE else "模型檔案不存在"
            print(f"[YOLOv8] {reason}，進入 Demo 模式")

    # ----------------------------------------------------------
    # 正式推論
    # ----------------------------------------------------------
    def detect(self, image_path: str, conf_threshold: float = 0.5) -> dict:
        """
        執行 YOLO Inference，回傳 Event JSON

        回傳格式：
        {
            "image": "path/to/image.jpg",
            "timestamp": "2026-04-05T10:30:00",
            "detections": [
                {
                    "class_id": 0,
                    "class_name": "Helmet",
                    "confidence": 0.94,
                    "bbox": [x1, y1, x2, y2]
                }
            ],
            "helmet_count": 3,
            "no_helmet_count": 1,
            "demo_mode": false
        }
        """
        if self.demo_mode:
            return self._demo_detect(image_path, conf_threshold)

        results = self.model(image_path, conf=conf_threshold, verbose=False)
        detections = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                detections.append({
                    "class_id": cls_id,
                    "class_name": self.CLASS_NAMES.get(cls_id, f"class_{cls_id}"),
                    "confidence": round(conf, 4),
                    "bbox": [round(v, 1) for v in xyxy],
                })

        helmet_count = sum(1 for d in detections if d["class_id"] == 0)
        no_helmet_count = sum(1 for d in detections if d["class_id"] == 1)

        return {
            "image": image_path,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "detections": detections,
            "helmet_count": helmet_count,
            "no_helmet_count": no_helmet_count,
            "demo_mode": False,
        }

    # ----------------------------------------------------------
    # 批次偵測
    # ----------------------------------------------------------
    def detect_batch(self, image_paths: list, conf_threshold: float = 0.5) -> list:
        """批次推論多張影像"""
        return [self.detect(p, conf_threshold) for p in image_paths]

    # ----------------------------------------------------------
    # 取得原始信心度（供 KMeans 校準使用）
    # ----------------------------------------------------------
    def get_raw_confidences(self, image_path: str) -> list:
        """取得所有偵測結果的原始信心度（不套用門檻）"""
        if self.demo_mode:
            return self._demo_confidences()

        results = self.model(image_path, conf=0.01, verbose=False)
        confidences = []
        for r in results:
            for box in r.boxes:
                confidences.append({
                    "class_id": int(box.cls[0]),
                    "confidence": float(box.conf[0]),
                })
        return confidences

    # ----------------------------------------------------------
    # Demo 模式：模擬偵測結果
    # ----------------------------------------------------------
    def _demo_detect(self, image_path: str, conf_threshold: float) -> dict:
        """模擬 YOLO 偵測結果（Demo 用）"""
        num_people = random.randint(2, 6)
        detections = []

        for i in range(num_people):
            has_helmet = random.random() > 0.35
            cls_id = 0 if has_helmet else 1
            conf = round(random.uniform(0.65, 0.99), 4) if has_helmet else round(random.uniform(0.55, 0.95), 4)

            if conf < conf_threshold:
                continue

            x1 = random.randint(50, 500)
            y1 = random.randint(50, 400)
            detections.append({
                "class_id": cls_id,
                "class_name": self.CLASS_NAMES[cls_id],
                "confidence": conf,
                "bbox": [x1, y1, x1 + random.randint(60, 120), y1 + random.randint(80, 160)],
            })

        helmet_count = sum(1 for d in detections if d["class_id"] == 0)
        no_helmet_count = sum(1 for d in detections if d["class_id"] == 1)

        return {
            "image": image_path,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "detections": detections,
            "helmet_count": helmet_count,
            "no_helmet_count": no_helmet_count,
            "demo_mode": True,
        }

    def _demo_confidences(self) -> list:
        """模擬原始信心度資料（供 KMeans Demo）"""
        confidences = []
        # 模擬雙峰分佈：高信心群 + 低信心群
        for _ in range(random.randint(15, 30)):
            if random.random() > 0.3:
                conf = round(random.gauss(0.85, 0.08), 4)
            else:
                conf = round(random.gauss(0.35, 0.12), 4)
            conf = max(0.01, min(0.99, conf))
            confidences.append({
                "class_id": random.choice([0, 1]),
                "confidence": conf,
            })
        return confidences
