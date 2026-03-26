# ============================================================
# AI-Guardian - Alert Models
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertType(str, Enum):
    TEMP_HIGH = "temperature_high"
    TEMP_CRITICAL = "temperature_critical"
    HUMIDITY_HIGH = "humidity_high"
    GAS_LEAK = "gas_leak"
    DUST_HIGH = "dust_high"
    WATER_LEAK = "water_leak"
    ELECTRIC_LEAK = "electric_leak"
    MOTION_DETECTED = "motion_detected"
    DOOR_OPEN = "door_open"
    FIRE = "fire"
    UPS_LOW = "ups_low"
    CONNECTION_LOST = "connection_lost"


class AlertCreate(BaseModel):
    type: AlertType
    severity: SeverityLevel
    message: str
    node: str = "esp32_sensor_node"
    sensor_reading: Optional[dict] = None
    triggered_value: Optional[float] = None
    threshold_value: Optional[float] = None


class AlertResponse(BaseModel):
    id: str
    type: AlertType
    severity: SeverityLevel
    message: str
    node: str
    sensor_reading: Optional[dict]
    triggered_value: Optional[float]
    threshold_value: Optional[float]
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    acknowledged_by: Optional[str] = None


class AlertListResponse(BaseModel):
    total: int
    alerts: List[AlertResponse]
