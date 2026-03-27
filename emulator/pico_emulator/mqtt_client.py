# ============================================================
# AI-Guardian - MQTT Client for Pico Emulator
# Uses paho-mqtt (replaces umqtt.simple from Pico)
# ============================================================

import json
import time
import threading
from typing import Optional, Callable
import paho.mqtt.client as mqtt

from . import config
from .emulator_core import PicoEmulatorCore


class PicoMQTTClient:
    """
    MQTT client cho Pico emulator - thay thế umqtt.simple của Pico.
    Sử dụng paho-mqtt với callback-based architecture.
    """

    def __init__(self, core: PicoEmulatorCore,
                 on_connect: Optional[Callable] = None,
                 on_disconnect: Optional[Callable] = None,
                 on_message: Optional[Callable] = None):
        self._core = core
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_message = on_message
        self._client: Optional[mqtt.Client] = None
        self._connected = False
        self._last_status_publish = 0.0
        self._running = False
        self._loop_thread: Optional[threading.Thread] = None

    def _create_client(self) -> mqtt.Client:
        """Tạo MQTT client với callbacks."""
        client = mqtt.Client(client_id=config.CLIENT_ID)
        client.username_pw_set(config.MQTT_USER, config.MQTT_PASS)
        client.on_connect = self._on_connect_cb
        client.on_disconnect = self._on_disconnect_cb
        client.on_message = self._on_message_cb
        return client

    def _on_connect_cb(self, client, userdata, flags, rc):
        """Callback khi kết nối MQTT thành công."""
        if rc == 0:
            self._connected = True
            client.subscribe(config.MQTT_TOPIC_ACTIONS)
            if self._on_connect:
                self._on_connect()
        else:
            self._connected = False

    def _on_disconnect_cb(self, client, userdata, rc):
        """Callback khi ngắt kết nối MQTT."""
        self._connected = False
        if self._on_disconnect:
            self._on_disconnect(rc)

    def _on_message_cb(self, client, userdata, msg):
        """Callback khi nhận được message MQTT."""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode('utf-8')
            data = json.loads(payload_str)

            if topic == config.MQTT_TOPIC_ACTIONS:
                action = data.get("action", "")
                priority = data.get("priority", "normal")
                devices = data.get("devices")

                self._core.handle_action(
                    action=action,
                    priority=priority,
                    devices=devices
                )
                self.publish_ack(action, "handled")

            if self._on_message:
                self._on_message(topic, data)

        except json.JSONDecodeError as e:
            print(f"[MQTT] JSON decode error: {e}")
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")

    def connect(self, broker: Optional[str] = None, port: Optional[int] = None,
                timeout: int = 10) -> bool:
        """Kết nối đến MQTT broker."""
        broker = broker or config.MQTT_BROKER
        port = port or config.MQTT_PORT

        self._client = self._create_client()

        try:
            result = self._client.connect(broker, port, keepalive=60)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self._running = True
                self._loop_thread = self._client.loop_start()
                return True
            return False
        except Exception as e:
            print(f"[MQTT] Connection error: {e}")
            return False

    def disconnect(self):
        """Ngắt kết nối MQTT."""
        self._running = False
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def is_connected(self) -> bool:
        """Kiểm tra trạng thái kết nối."""
        return self._connected

    def publish_ack(self, action: str, status: str):
        """Publish actuator acknowledgment."""
        if self._client and self._connected:
            payload = self._core.get_ack_payload(action, status)
            self._client.publish(
                config.MQTT_TOPIC_ACK,
                json.dumps(payload)
            )

    def publish_status(self):
        """Publish trạng thái actuator định kỳ."""
        if self._client and self._connected:
            payload = self._core.get_status_payload()
            self._client.publish(
                config.MQTT_TOPIC_STATUS,
                json.dumps(payload)
            )
            self._last_status_publish = time.time()

    def should_publish_status(self) -> bool:
        """Kiểm tra xem có nên publish status không."""
        return time.time() - self._last_status_publish >= config.STATUS_INTERVAL

    def reconnect(self) -> bool:
        """Thử kết nối lại."""
        if self._client:
            try:
                self._client.reconnect()
                return True
            except Exception as e:
                print(f"[MQTT] Reconnect error: {e}")
        return False
