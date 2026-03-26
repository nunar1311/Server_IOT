# ============================================================
# AI-Guardian - Pydantic Models for Sensor Data
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum


class SeverityLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SensorData(BaseModel):
    """Incoming sensor data from ESP32 node."""
    node: str = Field(default="esp32_sensor_node", description="Sensor node ID")
    temperature: float = Field(ge=-50, le=150, description="Temperature in Celsius")
    humidity: float = Field(ge=0, le=100, description="Relative humidity %")
    dust_pm25: float = Field(ge=0, description="PM2.5 in ug/m3")
    dust_pm10: Optional[float] = Field(default=None, ge=0, description="PM10 in ug/m3")
    gas: float = Field(ge=0, le=100, description="Gas/smoke level %")
    motion: bool = Field(default=False, description="PIR motion detected")
    door: bool = Field(default=False, description="Door open status")
    leak: bool = Field(default=False, description="Water leak detected")
    current_leak: float = Field(default=0.0, ge=0, description="Electric current leak (A)")
    voltage_input: float = Field(default=220.0, ge=0, description="Input voltage (V)")
    voltage_ups: float = Field(default=12.0, ge=0, description="UPS voltage (V)")
    rssi: Optional[int] = Field(default=None, description="WiFi signal strength")
    uptime: Optional[int] = Field(default=None, description="Node uptime in seconds")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class SensorDataCreate(SensorData):
    pass


class SensorDataResponse(BaseModel):
    id: str
    node: str
    temperature: float
    humidity: float
    dust_pm25: float
    dust_pm10: Optional[float]
    gas: float
    motion: bool
    door: bool
    leak: bool
    current_leak: float
    voltage_input: float
    voltage_ups: float
    rssi: Optional[int]
    uptime: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True


class SensorStats(BaseModel):
    """Aggregated sensor statistics."""
    node: str
    period: str
    avg_temperature: float
    avg_humidity: float
    avg_dust_pm25: float
    avg_gas: float
    max_temperature: float
    max_gas: float
    max_dust_pm25: float
    total_motion_events: int
    total_leak_events: int
    total_door_events: int
    record_count: int
