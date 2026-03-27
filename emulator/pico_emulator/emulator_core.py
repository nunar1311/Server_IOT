# ============================================================
# AI-Guardian - Pico RP2040 Emulator Core
# Core logic: relay state management + action handlers
# Ported from Pico RP2040 MicroPython code
# ============================================================

import time
from collections import defaultdict
from typing import Dict, List, Optional, Callable
from . import config


class PicoEmulatorCore:
    """
    Giả lập trạng thái actuator của Pico RP2040.
    Port chính xác logic từ Pico main.py.
    """

    def __init__(self, on_state_change: Optional[Callable] = None,
                 on_action: Optional[Callable] = None,
                 on_alarm: Optional[Callable] = None):
        self._relay_state: Dict[str, bool] = {name: False for name in config.RELAY_MAP}
        self._start_time = time.time()
        self._last_action: Optional[str] = None
        self._last_action_time = 0.0
        self._action_count: Dict[str, int] = defaultdict(int)
        self._action_history: List[Dict] = []
        self._on_state_change = on_state_change
        self._on_action = on_action
        self._on_alarm = on_alarm

    def set_actuator(self, name: str, state: bool) -> bool:
        """Set trạng thái relay ảo."""
        if name in self._relay_state:
            old_state = self._relay_state[name]
            self._relay_state[name] = state
            self._last_action = name
            self._last_action_time = time.time()
            if self._on_state_change:
                self._on_state_change(name, state, old_state)
            return True
        return False

    def get_actuator(self, name: str) -> Optional[bool]:
        """Lấy trạng thái một relay."""
        return self._relay_state.get(name)

    def all_off(self):
        """Tắt tất cả relay ảo."""
        for name in list(self._relay_state.keys()):
            self.set_actuator(name, False)

    def all_on(self):
        """Bật tất cả relay ảo (dùng cẩn thận)."""
        for name in list(self._relay_state.keys()):
            self.set_actuator(name, True)

    def get_state(self) -> Dict[str, bool]:
        """Lấy trạ thái tất cả relay."""
        return self._relay_state.copy()

    def get_on_devices(self) -> List[str]:
        """Danh sách thiết bị đang bật."""
        return [name for name, state in self._relay_state.items() if state]

    def get_uptime(self) -> int:
        """Lấy uptime tính bằng giây."""
        return int(time.time() - self._start_time)

    def get_action_history(self, limit: int = 20) -> List[Dict]:
        """Lấy lịch sử actions gần đây."""
        return self._action_history[-limit:]

    def _log_action(self, action: str, priority: str, devices: Dict):
        """Ghi log action."""
        entry = {
            "action": action,
            "priority": priority,
            "devices": devices,
            "timestamp": time.time(),
            "state_snapshot": self.get_state()
        }
        self._action_history.append(entry)
        self._action_count[action] += 1

    def handle_action(self, action: str, priority: str = "normal", devices: dict = None):
        """
        Xử lý action - giữ nguyên logic từ Pico main.py.
        PORT CHÍNH XÁC từ Pico RP2040 main.py
        """
        if self._on_action:
            self._on_action(action, priority)

        if action == "fire":
            self._handle_fire(priority)
        elif action == "flood":
            self._handle_flood(priority)
        elif action == "gas_leak":
            self._handle_gas_leak(priority)
        elif action == "electric_leak":
            self._handle_electric_leak(priority)
        elif action == "intrusion":
            self._handle_intrusion(priority)
        elif action == "temp_high":
            self._handle_temp_high(priority)
        elif action == "clear":
            self._handle_clear()
        elif action == "reset":
            self._handle_reset()
        elif action == "manual":
            self._handle_manual(devices or {})
        else:
            pass  # Unknown action - ignore

        self._log_action(action, priority, devices or {})

    def _handle_fire(self, priority: str):
        """Xử lý action fire - PORT từ Pico main.py line 139-148."""
        self.set_actuator("buzzer", True)
        if self._on_alarm:
            self._on_alarm("emergency")
        self.set_actuator("warning_light", True)
        time.sleep(0.5)
        self.set_actuator("co2", True)
        self.set_actuator("fan", True)
        if priority == "critical":
            self.set_actuator("power_cut", True)

    def _handle_flood(self, priority: str):
        """Xử lý action flood - PORT từ Pico main.py line 150-157."""
        self.set_actuator("buzzer", True)
        if self._on_alarm:
            self._on_alarm("warning")
        self.set_actuator("pump", True)
        self.set_actuator("warning_light", True)
        if priority == "critical":
            self.set_actuator("power_cut", True)

    def _handle_gas_leak(self, priority: str):
        """Xử lý action gas_leak - PORT từ Pico main.py line 159-166."""
        self.set_actuator("buzzer", True)
        if self._on_alarm:
            self._on_alarm("emergency")
        self.set_actuator("fan", True)
        self.set_actuator("warning_light", True)
        if priority == "critical":
            self.set_actuator("power_cut", True)

    def _handle_electric_leak(self, priority: str):
        """Xử lý action electric_leak - PORT từ Pico main.py line 168-174."""
        self.set_actuator("buzzer", True)
        if self._on_alarm:
            self._on_alarm("emergency")
        self.set_actuator("warning_light", True)
        time.sleep(0.3)
        self.set_actuator("power_cut", True)

    def _handle_intrusion(self, priority: str):
        """Xử lý action intrusion - PORT từ Pico main.py line 176-181."""
        self.set_actuator("buzzer", True)
        if self._on_alarm:
            self._on_alarm("warning")
        self.set_actuator("warning_light", True)
        self.set_actuator("door_lock", True)

    def _handle_temp_high(self, priority: str):
        """Xử lý action temp_high - PORT từ Pico main.py line 183-188."""
        self.set_actuator("fan", True)
        if priority == "critical":
            self.set_actuator("buzzer", True)
            self.set_actuator("warning_light", True)

    def _handle_clear(self):
        """Xử lý action clear - PORT từ Pico main.py line 190-193."""
        self.all_off()
        if self._on_alarm:
            self._on_alarm("ok")

    def _handle_reset(self):
        """Xử lý action reset - PORT từ Pico main.py line 195-197."""
        self.all_off()

    def _handle_manual(self, devices: Dict[str, bool]):
        """Xử lý action manual - PORT từ Pico main.py line 199-202."""
        for key, val in devices.items():
            self.set_actuator(key, bool(val))

    def get_status_payload(self) -> Dict:
        """Tạo payload status để publish MQTT."""
        return {
            "node": config.CLIENT_ID,
            "state": self.get_state(),
            "uptime": self.get_uptime(),
            "last_action": self._last_action,
            "action_counts": dict(self._action_count)
        }

    def get_ack_payload(self, action: str, status: str) -> Dict:
        """Tạo payload ack để publish MQTT."""
        return {
            "node": config.CLIENT_ID,
            "action": action,
            "status": status,
            "actuators": self.get_state()
        }
