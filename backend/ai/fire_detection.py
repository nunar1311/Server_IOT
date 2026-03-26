# ============================================================
# AI-Guardian - Fire Detection Module
# Phat hien chay dua tren nhiet do, khi gas, va hinh anh
# ============================================================

from typing import Dict, Any, Optional, Tuple
import math

class FireDetector:
    """
    Phat hien chay bang cach phan tich nhieu nguon:
    - Nhiet do tang nhanh
    - Muc gas/khoi cao
    - Du lieu tu ESP32-CAM
    """

    def __init__(self):
        self._last_temp = None
        self._temp_history = []
        self._gas_baseline = 5.0

    def analyze_temperature_rate(self, temp: float, threshold_rate: float = 3.0) -> Optional[Dict]:
        """
        Phat hien tang nhiet do nhanh bat thuong.
        threshold_rate: do C/phut
        """
        self._temp_history.append(temp)
        if len(self._temp_history) > 10:
            self._temp_history.pop(0)
        if len(self._temp_history) >= 2:
            delta = temp - self._temp_history[-2]
            if delta > threshold_rate:
                return {
                    "detected": True,
                    "type": "rapid_temperature_rise",
                    "current_temp": temp,
                    "rate_of_rise": round(delta, 2),
                    "severity": "critical"
                }
        return None

    def analyze_combined_risk(
        self,
        temp: float,
        gas: float,
        humidity: float,
        dust: float
    ) -> Tuple[bool, float, Dict]:
        """
        Phan tich rui ro chay theo nhieu yeu to.
        Tra ve (is_fire, risk_score, details)
        """
        risk_score = 0.0
        details = {}
        if temp >= 70:
            risk_score += 0.5
            details["temp_critical"] = True
        elif temp >= 55:
            risk_score += 0.35
        elif temp >= 45:
            risk_score += 0.2
            details["temp_warning"] = True
        if gas >= 80:
            risk_score += 0.4
            details["gas_critical"] = True
        elif gas >= 60:
            risk_score += 0.25
        elif gas >= 40:
            risk_score += 0.1
        if dust >= 100:
            risk_score += 0.3
            details["smoke_detected"] = True
        if humidity < 30:
            risk_score += 0.1
            details["low_humidity"] = True
        is_fire = risk_score >= 0.6
        return is_fire, round(risk_score, 3), details

    def evaluate(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate fire risk from sensor data.
        Returns detection result or None if safe.
        """
        temp = data.get("temperature", 25)
        gas = data.get("gas", 0)
        humidity = data.get("humidity", 50)
        dust = data.get("dust_pm25", 0)

        rate_alert = self.analyze_temperature_rate(temp)
        is_fire, risk_score, details = self.analyze_combined_risk(temp, gas, humidity, dust)

        result = {
            "is_fire": is_fire,
            "risk_score": risk_score,
            "details": details,
            "temperature": temp,
            "gas": gas,
            "dust": dust,
            "humidity": humidity
        }

        if rate_alert:
            result["rapid_temp_rise"] = rate_alert
            result["is_fire"] = True
            result["risk_score"] = 1.0

        return result


_detector: Optional[FireDetector] = None


def get_fire_detector() -> FireDetector:
    global _detector
    if _detector is None:
        _detector = FireDetector()
    return _detector
