"""
threshold.py -- KMeans 自動校準信心度門檻

職責：
  收集 YOLO 偵測的原始信心度 → KMeans 非監督分群 →
  自動計算最佳門檻（取代人工設定）

原理：
  YOLOv8 偵測結果的信心度呈雙峰分佈：
    - 高信心群：正確偵測（安全帽 / 未戴安全帽）
    - 低信心群：誤偵測、背景雜訊
  用 KMeans(n_clusters=2) 將信心度分為兩群，
  取兩群中心點的中點作為最佳門檻。
"""

import numpy as np
from sklearn.cluster import KMeans


class ThresholdCalibrator:
    """KMeans 信心度門檻自動校準器"""

    def __init__(self):
        self.history: list[float] = []
        self.current_threshold: float = 0.5  # 預設門檻
        self.calibration_log: list[dict] = []

    def add_confidences(self, confidences: list[float]):
        """累積信心度資料"""
        self.history.extend(confidences)

    def calibrate(self, min_samples: int = 10) -> dict:
        """
        執行 KMeans 校準

        回傳：
        {
            "old_threshold": 0.5,
            "new_threshold": 0.62,
            "cluster_centers": [0.32, 0.87],
            "sample_count": 50,
            "high_cluster_size": 35,
            "low_cluster_size": 15
        }
        """
        if len(self.history) < min_samples:
            return {
                "status": "insufficient_data",
                "sample_count": len(self.history),
                "min_required": min_samples,
                "current_threshold": self.current_threshold,
            }

        X = np.array(self.history).reshape(-1, 1)
        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(X)

        centers = sorted(kmeans.cluster_centers_.flatten().tolist())
        labels = kmeans.labels_

        # 門檻 = 兩群中心的中點
        old_threshold = self.current_threshold
        new_threshold = round((centers[0] + centers[1]) / 2, 4)
        self.current_threshold = new_threshold

        # 統計各群數量
        low_label = 0 if centers[0] < centers[1] else 1
        low_count = int(np.sum(labels == low_label))
        high_count = int(np.sum(labels != low_label))

        result = {
            "status": "calibrated",
            "old_threshold": round(old_threshold, 4),
            "new_threshold": new_threshold,
            "cluster_centers": [round(c, 4) for c in centers],
            "sample_count": len(self.history),
            "high_cluster_size": high_count,
            "low_cluster_size": low_count,
        }

        self.calibration_log.append(result)
        return result

    def get_threshold(self) -> float:
        """取得目前門檻"""
        return self.current_threshold

    def get_stats(self) -> dict:
        """取得校準統計"""
        return {
            "current_threshold": self.current_threshold,
            "total_samples": len(self.history),
            "calibration_count": len(self.calibration_log),
            "calibration_log": self.calibration_log[-5:],  # 最近 5 次
        }
