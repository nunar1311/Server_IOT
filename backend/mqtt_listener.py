# ============================================================
# AI-Guardian - MQTT Listener Service
# ============================================================

import json
import asyncio
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import paho.mqtt.client as mqtt
from database import get_collections, DatabaseCollections
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MQTTListener:
    """MQTT listener that processes sensor data and triggers alerts/actions."""

    BROKER = "localhost"
    PORT = 1883
    USERNAME = "mqtt_user"
    PASSWORD = "mqtt_password"

    TOPICS = {
        "sensors": "ai-guardian/sensors",
        "actions": "ai-guardian/actions",
        "status": "ai-guardian/status",
        "actuator_status": "ai-guardian/actuator/status",
        "actuator_ack": "ai-guardian/actuator/ack",
        "camera": "ai-guardian/camera",
        "camera_alert": "ai-guardian/camera/alert",
    }

    def __init__(self):
        self._client: Optional[mqtt.Client] = None
        self._db: Optional[DatabaseCollections] = None
        self._action_callbacks: Dict[str, Callable] = {}
        self._running = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected successfully")
            for topic in self.TOPICS.values():
                client.subscribe(topic)
                logger.info(f"Subscribed to: {topic}")
        else:
            logger.error(f"MQTT connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())

            if topic == self.TOPICS["sensors"]:
                self._handle_sensor_data(payload)
            elif topic == self.TOPICS["camera"]:
                self._handle_camera_data(payload)
            elif topic == self.TOPICS["camera_alert"]:
                self._handle_camera_alert(payload)
            elif topic == self.TOPICS["status"]:
                self._handle_status(payload)
            elif topic == self.TOPICS["actuator_ack"]:
                self._handle_actuator_ack(payload)

        except json.JSONDecodeError:
            logger.error(f"Failed to parse MQTT message: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def _handle_sensor_data(self, data: Dict[str, Any]):
        """Process incoming sensor data."""
        if self._db is None:
            self._db = get_collections()

        data["received_at"] = datetime.utcnow()
        self._db.sensor_logs.insert_one(data)
        logger.debug(f"Sensor data stored: {data.get('node', 'unknown')}")

        alerts = self._check_thresholds(data)
        for alert in alerts:
            self._db.alerts.insert_one(alert)
            logger.warning(f"ALERT: {alert['type']} - {alert['message']}")

        for callback in self._action_callbacks.values():
            for alert in alerts:
                callback(alert)

    def _handle_camera_data(self, data: Dict[str, Any]):
        """Process camera metadata."""
        if self._db is None:
            self._db = get_collections()
        data["received_at"] = datetime.utcnow()
        logger.debug(f"Camera frame: {data.get('node', 'unknown')}")

    def _handle_camera_alert(self, data: Dict[str, Any]):
        """Process camera alerts."""
        if self._db is None:
            self._db = get_collections()
        data["received_at"] = datetime.utcnow()
        self._db.camera_alerts.insert_one(data)
        self._db.alerts.insert_one({
            "type": f"camera_{data.get('alert_type', 'unknown')}",
            "severity": "critical",
            "message": f"Camera AI detected: {data.get('alert_type')}",
            "node": data.get("node", "esp32_cam"),
            "sensor_reading": data,
            "created_at": datetime.utcnow()
        })
        logger.warning(f"CAMERA ALERT: {data.get('alert_type')}")

    def _handle_status(self, data: Dict[str, Any]):
        """Handle status updates from nodes."""
        logger.info(f"Status from {data.get('node')}: {data.get('status')}")

    def _handle_actuator_ack(self, data: Dict[str, Any]):
        """Handle actuator acknowledgment."""
        if self._db is None:
            self._db = get_collections()
        data["received_at"] = datetime.utcnow()
        self._db.actuator_logs.insert_one(data)
        logger.info(f"Actuator ack: {data.get('action')} -> {data.get('status')}")

    def _check_thresholds(self, data: Dict[str, Any]) -> list:
        """Check sensor values against thresholds and generate alerts."""
        alerts = []
        now = datetime.utcnow()
        temp = data.get("temperature", 0)
        gas = data.get("gas", 0)
        dust = data.get("dust_pm25", 0)
        leak = data.get("leak", False)
        door = data.get("door", False)
        motion = data.get("motion", False)
        current_leak = data.get("current_leak", 0)
        voltage_ups = data.get("voltage_ups", 12)

        if temp >= 55:
            alerts.append({
                "type": "temperature_critical",
                "severity": "emergency",
                "message": f"CRITICAL: Temperature {temp}C exceeds 55C",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": temp,
                "threshold_value": 55.0,
                "created_at": now
            })
        elif temp >= 45:
            alerts.append({
                "type": "temperature_high",
                "severity": "warning",
                "message": f"WARNING: Temperature {temp}C exceeds 45C",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": temp,
                "threshold_value": 45.0,
                "created_at": now
            })

        if gas >= 80:
            alerts.append({
                "type": "gas_leak",
                "severity": "emergency",
                "message": f"CRITICAL: Gas level {gas}% exceeds 80%",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": gas,
                "threshold_value": 80.0,
                "created_at": now
            })
        elif gas >= 60:
            alerts.append({
                "type": "gas_leak",
                "severity": "warning",
                "message": f"WARNING: Gas level {gas}% exceeds 60%",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": gas,
                "threshold_value": 60.0,
                "created_at": now
            })

        if dust >= 75:
            alerts.append({
                "type": "dust_high",
                "severity": "critical",
                "message": f"CRITICAL: PM2.5 dust {dust}ug/m3 exceeds 75",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": dust,
                "threshold_value": 75.0,
                "created_at": now
            })
        elif dust >= 35:
            alerts.append({
                "type": "dust_high",
                "severity": "warning",
                "message": f"WARNING: PM2.5 dust {dust}ug/m3 exceeds 35",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": dust,
                "threshold_value": 35.0,
                "created_at": now
            })

        if leak:
            alerts.append({
                "type": "water_leak",
                "severity": "critical",
                "message": "WATER LEAK DETECTED!",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "created_at": now
            })

        if current_leak >= 5:
            alerts.append({
                "type": "electric_leak",
                "severity": "emergency",
                "message": f"CRITICAL: Electric leak {current_leak}A exceeds 5A",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": current_leak,
                "threshold_value": 5.0,
                "created_at": now
            })
        elif current_leak >= 3:
            alerts.append({
                "type": "electric_leak",
                "severity": "warning",
                "message": f"WARNING: Electric leak {current_leak}A exceeds 3A",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": current_leak,
                "threshold_value": 3.0,
                "created_at": now
            })

        if voltage_ups < 11:
            alerts.append({
                "type": "ups_low",
                "severity": "critical",
                "message": f"CRITICAL: UPS voltage {voltage_ups}V below 11V",
                "node": data.get("node", "esp32_sensor_node"),
                "sensor_reading": data,
                "triggered_value": voltage_ups,
                "threshold_value": 11.0,
                "created_at": now
            })

        return alerts

    def register_action_callback(self, name: str, callback: Callable):
        """Register a callback to be called when alerts are generated."""
        self._action_callbacks[name] = callback

    def unregister_action_callback(self, name: str):
        """Remove a registered callback."""
        self._action_callbacks.pop(name, None)

    def publish_action(self, action: str, priority: str = "normal", devices: dict = None):
        """Publish an action command to MQTT."""
        if self._client and self._client.is_connected():
            payload = {
                "action": action,
                "priority": priority,
                "timestamp": datetime.utcnow().isoformat()
            }
            if devices:
                payload["devices"] = devices
            self._client.publish(
                self.TOPICS["actions"],
                json.dumps(payload)
            )
            logger.info(f"Published action: {action} (priority: {priority})")

    def start(self):
        """Start the MQTT listener (blocking)."""
        self._client = mqtt.Client()
        self._client.username_pw_set(self.USERNAME, self.PASSWORD)
        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

        try:
            self._client.connect(self.BROKER, self.PORT, 60)
            self._running = True
            self._client.loop_forever()
        except Exception as e:
            logger.error(f"MQTT connection error: {e}")

    def stop(self):
        """Stop the MQTT listener."""
        self._running = False
        if self._client:
            self._client.disconnect()


_listener: Optional[MQTTListener] = None


def get_mqtt_listener() -> MQTTListener:
    global _listener
    if _listener is None:
        _listener = MQTTListener()
    return _listener
