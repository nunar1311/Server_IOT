# ============================================================
# AI-Guardian - Anomaly Detection Module
# Su dung Isolation Forest de phat hien bat thuong
# ============================================================

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os

class AnomalyDetector:
    """
    Phat hien bat thuong trong du lieu cam bien bang Isolation Forest.
    """

    FEATURE_NAMES = [
        "temperature", "humidity", "dust_pm25", "gas",
        "current_leak", "voltage_input"
    ]

    def __init__(self, contamination: float = 0.05, model_path: str = None):
        self.contamination = contamination
        self.model: Optional[IsolationForest] = None
        self.scaler = StandardScaler()
        self._is_fitted = False
        self._threshold = 0.5

        if model_path and os.path.exists(model_path):
            self.load(model_path)

    def _extract_features(self, data: Dict[str, Any]) -> np.ndarray:
        """Extract and order features from sensor data dict."""
        features = []
        for name in self.FEATURE_NAMES:
            val = data.get(name, 0.0)
            if val is None:
                val = 0.0
            features.append(float(val))
        return np.array(features).reshape(1, -1)

    def fit(self, historical_data: List[Dict[str, Any]]) -> "AnomalyDetector":
        """Train anomaly detector on historical data."""
        if len(historical_data) < 50:
            return self

        X = np.vstack([self._extract_features(d) for d in historical_data])
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)

        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=100,
            max_samples="auto",
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        self._is_fitted = True
        return self

    def detect(self, data: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Kiem tra xem du lieu co bat thuong khong.
        Tra ve (is_anomaly, anomaly_score)
        """
        if not self._is_fitted or self.model is None:
            return self._rule_based_check(data)

        features = self._extract_features(data)
        features_scaled = self.scaler.transform(features)
        prediction = self.model.predict(features_scaled)[0]
        score = abs(self.model.score_samples(features_scaled)[0])
        return prediction == -1, score

    def _rule_based_check(self, data: Dict[str, Any]) -> Tuple[bool, float]:
        """Fallback rule-based detection."""
        score = 0.0
        temp = data.get("temperature", 25)
        gas = data.get("gas", 0)
        dust = data.get("dust_pm25", 0)
        leak = data.get("leak", False)
        current = data.get("current_leak", 0)

        if temp > 55: score += 0.5
        elif temp > 45: score += 0.3
        if gas > 80: score += 0.5
        elif gas > 60: score += 0.3
        if dust > 75: score += 0.4
        elif dust > 35: score += 0.2
        if leak: score += 0.5
        if current > 5: score += 0.5
        elif current > 3: score += 0.3

        return score > 0.5, score

    def get_anomaly_features(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Return feature importance contribution to anomaly."""
        is_anomaly, score = self.detect(data)
        if not is_anomaly:
            return {}
        contributions = {}
        temp = data.get("temperature", 0)
        gas = data.get("gas", 0)
        dust = data.get("dust_pm25", 0)
        leak = data.get("leak", 0)
        current = data.get("current_leak", 0)

        if temp > 45: contributions["temperature"] = temp
        if gas > 60: contributions["gas"] = gas
        if dust > 35: contributions["dust_pm25"] = dust
        if leak: contributions["leak"] = 1.0
        if current > 3: contributions["current_leak"] = current
        return contributions

    def save(self, path: str):
        """Save model to disk."""
        if self.model:
            joblib.dump({
                "model": self.model,
                "scaler": self.scaler,
                "contamination": self.contamination,
                "is_fitted": self._is_fitted
            }, path)

    def load(self, path: str):
        """Load model from disk."""
        if os.path.exists(path):
            data = joblib.load(path)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.contamination = data["contamination"]
            self._is_fitted = data["is_fitted"]


# Global instance
_detector: Optional[AnomalyDetector] = None


def get_anomaly_detector() -> AnomalyDetector:
    global _detector
    if _detector is None:
        _detector = AnomalyDetector()
    return _detector


def detect_anomaly(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Convenience function to detect anomaly in sensor data."""
    detector = get_anomaly_detector()
    is_anomaly, score = detector.detect(data)
    if is_anomaly:
        return {
            "is_anomaly": True,
            "score": float(score),
            "contributing_features": detector.get_anomaly_features(data)
        }
    return None
