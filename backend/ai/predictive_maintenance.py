# ============================================================
# AI-Guardian - Predictive Maintenance Module
# Du doan thiet bi sap bi hong dua tren lich su
# ============================================================

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque
from sklearn.linear_model import LinearRegression

class PredictiveMaintenance:
    """
    Du doan thiet bi sap hong bang cach phan tich xu huong
    va thoi gian su dung.
    """

    def __init__(self):
        self._temp_history = deque(maxlen=288)   # 24h at 5min intervals
        self._hum_history = deque(maxlen=288)
        self._gas_history = deque(maxlen=288)
        self._dust_history = deque(maxlen=288)
        self._current_history = deque(maxlen=288)
        self._vibration_history = deque(maxlen=288)
        self._device_uptimes: Dict[str, int] = {}
        self._device_events: Dict[str, List[Dict]] = {}

    def add_reading(self, data: Dict[str, Any]):
        """Add a sensor reading to history."""
        self._temp_history.append(data.get("temperature", 25))
        self._hum_history.append(data.get("humidity", 50))
        self._gas_history.append(data.get("gas", 0))
        self._dust_history.append(data.get("dust_pm25", 0))
        self._current_history.append(data.get("current_leak", 0))

    def _fit_trend(self, history: deque) -> Optional[Tuple[float, float]]:
        """Fit linear regression to detect trend."""
        if len(history) < 24:
            return None
        X = np.arange(len(history)).reshape(-1, 1)
        y = np.array(list(history))
        model = LinearRegression()
        model.fit(X, y)
        return model.coef_[0], model.intercept_

    def predict_temperature_failure(self, hours_ahead: int = 6) -> Optional[Dict]:
        """Predict if temperature will exceed critical threshold."""
        trend = self._fit_trend(self._temp_history)
        if not trend:
            return None
        slope, intercept = trend
        current_len = len(self._temp_history)
        future_idx = current_len + (hours_ahead * 12)
        predicted = slope * future_idx + intercept
        if predicted > 55:
            return {
                "type": "temperature_critical",
                "predicted_value": round(predicted, 2),
                "threshold": 55,
                "hours_until_failure": round((55 - intercept) / slope / 12, 1) if slope > 0 else None,
                "confidence": "medium",
                "trend": "rising" if slope > 0.1 else "stable"
            }
        return None

    def predict_gas_leak(self) -> Optional[Dict]:
        """Predict if gas levels are trending dangerous."""
        trend = self._fit_trend(self._gas_history)
        if not trend:
            return None
        slope, intercept = trend
        if slope > 0.5 and intercept + slope * len(self._gas_history) > 60:
            return {
                "type": "gas_leak_rising",
                "trend_slope": round(slope, 4),
                "current_value": round(self._gas_history[-1], 2),
                "predicted_value_1h": round(intercept + slope * (len(self._gas_history) + 12), 2),
                "confidence": "low" if len(self._gas_history) < 100 else "medium"
            }
        return None

    def calculate_component_health(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Tinh toan doi tuoi cua tung thanh phan (0-100%).
        100% = tot, 0% = hong.
        """
        health = {}
        temp = data.get("temperature", 25)
        health["temperature_sensor"] = max(0, 100 - max(0, (temp - 40) * 5))
        hum = data.get("humidity", 50)
        health["humidity_sensor"] = max(0, 100 - abs(hum - 50) * 1.5)
        gas = data.get("gas", 0)
        health["gas_sensor"] = max(0, 100 - gas * 0.8)
        dust = data.get("dust_pm25", 0)
        health["dust_sensor"] = max(0, 100 - dust * 1.5)
        current = data.get("current_leak", 0)
        health["electrical_system"] = max(0, 100 - current * 12)
        uptime = data.get("uptime", 0)
        if uptime > 0:
            days = uptime / 86400
            health["overall"] = max(0, 100 - days * 0.1)
        else:
            health["overall"] = 85.0
        return {k: round(v, 1) for k, v in health.items()}

    def get_maintenance_alerts(self) -> List[Dict[str, Any]]:
        """Generate maintenance recommendations based on analysis."""
        alerts = []
        temp_trend = self._fit_trend(self._temp_history)
        if temp_trend and temp_trend[0] > 0.3:
            alerts.append({
                "type": "maintenance",
                "priority": "medium",
                "message": f"Temperature trending upward (slope: {temp_trend[0]:.3f}). Check cooling system."
            })
        gas_trend = self._fit_trend(self._gas_history)
        if gas_trend and gas_trend[0] > 0.2:
            alerts.append({
                "type": "maintenance",
                "priority": "high",
                "message": f"Gas levels trending up (slope: {gas_trend[0]:.3f}). Inspect seals and vents."
            })
        avg_current = np.mean(list(self._current_history)) if self._current_history else 0
        if avg_current > 2.5:
            alerts.append({
                "type": "maintenance",
                "priority": "high",
                "message": f"Elevated average current leak ({avg_current:.2f}A). Check wiring insulation."
            })
        return alerts


_predictor: Optional[PredictiveMaintenance] = None


def get_predictor() -> PredictiveMaintenance:
    global _predictor
    if _predictor is None:
        _predictor = PredictiveMaintenance()
    return _predictor
