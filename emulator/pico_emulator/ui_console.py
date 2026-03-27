# ============================================================
# AI-Guardian - Console UI for Pico Emulator
# ANSI colored console output with box drawing characters
# ============================================================

import sys
import os
import time
from collections import deque
from typing import Optional, List, Dict

# ANSI Color Codes
class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground colors
    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    # Background colors
    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

    # Bright foreground
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"


# Action colors
ACTION_COLORS = {
    "fire":           (Colors.BG_RED,     Colors.BRIGHT_WHITE),
    "flood":          (Colors.BG_BLUE,    Colors.BRIGHT_WHITE),
    "gas_leak":       (Colors.BG_YELLOW,  Colors.BLACK),
    "electric_leak":  (Colors.BG_MAGENTA, Colors.BRIGHT_WHITE),
    "intrusion":      (Colors.BG_CYAN,    Colors.BLACK),
    "temp_high":      (Colors.BG_YELLOW,  Colors.BLACK),
    "clear":          (Colors.BG_GREEN,   Colors.BLACK),
    "reset":          (Colors.BG_GREEN,   Colors.BLACK),
    "manual":         (Colors.BG_BLUE,    Colors.BRIGHT_WHITE),
}

# Relay status colors
RELAY_ON_COLOR  = Colors.BRIGHT_GREEN
RELAY_OFF_COLOR = Colors.DIM + Colors.WHITE


def supports_ansi() -> bool:
    """Kiểm tra terminal có hỗ trợ ANSI không."""
    return sys.platform != "win32" or os.environ.get("ANSICON") or \
           hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class ConsoleUI:
    """
    Console UI đẹp cho Pico Emulator.
    Sử dụng ANSI escape codes để tô màu và vẽ khung.
    """

    def __init__(self, max_log_lines: int = 8):
        self._max_log_lines = max_log_lines
        self._log_entries: deque = deque(maxlen=max_log_lines)
        self._action_entries: deque = deque(maxlen=6)
        self._last_state: Optional[Dict[str, bool]] = None
        self._connected = False
        self._last_render_time = 0.0
        self._render_interval = 0.5  # seconds between renders
        self._ansi = supports_ansi()

    def _color(self, fg: str = "", bg: str = "", bold: bool = False) -> str:
        """Tạo ANSI escape sequence."""
        if not self._ansi:
            return ""
        result = bg + fg
        if bold:
            result = Colors.BOLD + result
        return result

    def _reset(self) -> str:
        """Reset ANSI formatting."""
        if not self._ansi:
            return ""
        return Colors.RESET

    def _timestamp(self) -> str:
        """Lấy timestamp hiện tại."""
        return time.strftime("%H:%M:%S")

    def _render_header(self) -> str:
        """Vẽ header."""
        lines = []
        line1 = self._color(Colors.BRIGHT_CYAN, bold=True) + \
                "  AI-Guardian Pico RP2040 Emulator  " + \
                self._reset() + \
                self._color(Colors.BRIGHT_WHITE, Colors.BG_BLUE) + \
                " [WINDOWS] " + \
                self._reset()

        conn_color = Colors.BRIGHT_GREEN if self._connected else Colors.BRIGHT_RED
        conn_text = "CONNECTED" if self._connected else "DISCONNECTED"
        line2 = self._color(conn_color, bold=True) + \
                f"  MQTT: {conn_text}  " + \
                self._reset()

        border = self._color(Colors.CYAN) + "+" + "-" * 40 + "+" + "-" * 38 + "+" + self._reset()

        lines.append(border)
        lines.append(f"|{self._color(Colors.BRIGHT_CYAN, Colors.BG_BLUE, bold=True):^79}|")
        lines.append(border)
        return "\n".join(lines)

    def _render_relay_table(self, state: Dict[str, bool]) -> str:
        """Vẽ bảng trạng thái relay."""
        from . import config

        lines = []
        header = self._color(Colors.WHITE, Colors.BG_BLUE, bold=True) + \
                 f"{'Relay Status':^39}|{'Relay Status':^38}" + \
                 self._reset()
        lines.append(self._color(Colors.CYAN) + "+" + "-" * 39 + "+" + "-" * 38 + "+" + self._reset())
        lines.append(header)
        lines.append(self._color(Colors.CYAN) + "+" + "-" * 39 + "+" + "-" * 38 + "+" + self._reset())

        names = list(config.RELAY_MAP.keys())
        half = (len(names) + 1) // 2

        for i in range(half):
            left_name = names[i]
            right_name = names[i + half] if (i + half) < len(names) else ""

            left_state = state.get(left_name, False)
            right_state = state.get(right_name, False) if right_name else False

            left_color = RELAY_ON_COLOR if left_state else RELAY_OFF_COLOR
            right_color = RELAY_ON_COLOR if right_state else RELAY_OFF_COLOR
            left_text = f"{'ON' if left_state else 'OFF'}"
            right_text = f"{'ON' if right_state else 'OFF'}"

            left_desc = config.RELAY_DESCRIPTIONS.get(left_name, left_name)
            right_desc = config.RELAY_DESCRIPTIONS.get(right_name, right_name) if right_name else ""

            gp_left = config.RELAY_MAP.get(left_name, "?")
            gp_right = config.RELAY_MAP.get(right_name, "?") if right_name else ""

            left_cell = f" GP{gp_left} {left_desc:<15} {left_color + left_text + self._reset():^7}"
            right_cell = f" GP{gp_right} {right_desc:<15} {right_color + right_text + self._reset():^7}" if right_name else " " * 38

            lines.append(f"|{left_cell}|{right_cell}|")

        lines.append(self._color(Colors.CYAN) + "+" + "-" * 39 + "+" + "-" * 38 + "+" + self._reset())
        return "\n".join(lines)

    def _render_action_log(self) -> str:
        """Vẽ bảng action log."""
        lines = []
        header = self._color(Colors.WHITE, Colors.BG_MAGENTA, bold=True) + \
                 f"{'Action Log':^77}" + \
                 self._reset()
        lines.append(self._color(Colors.MAGENTA) + "+" + "-" * 77 + "+" + self._reset())
        lines.append(header)
        lines.append(self._color(Colors.MAGENTA) + "+" + "+".join(["-" * 25, "-" * 25, "-" * 25]) + "+" + self._reset())

        header_row = self._color(Colors.BRIGHT_WHITE, bold=True) + \
                     f"{'TIME':^25}|{'ACTION':^25}|{'PRIORITY':^25}" + \
                     self._reset()
        lines.append(header_row)
        lines.append(self._color(Colors.MAGENTA) + "+" + "+".join(["-" * 25, "-" * 25, "-" * 25]) + "+" + self._reset())

        if not self._action_entries:
            lines.append(self._color(Colors.DIM) + f"|{'No actions yet':^77}|" + self._reset())
        else:
            for entry in reversed(list(self._action_entries)):
                ts = entry.get("time", "")
                action = entry.get("action", "")
                priority = entry.get("priority", "")

                bg, fg = ACTION_COLORS.get(action, (Colors.BG_BLACK, Colors.WHITE))

                action_cell = self._color(fg, bg, bold=True) + f"{action:^25}" + self._reset()
                priority_cell = self._color(Colors.BRIGHT_WHITE) + f"{priority:^25}" + self._reset()

                lines.append(f"|{self._color(Colors.YELLOW) + ts:^25}{self._reset()}|{action_cell}|{priority_cell}|")

        lines.append(self._color(Colors.MAGENTA) + "+" + "-" * 77 + "+" + self._reset())
        return "\n".join(lines)

    def _render_mqtt_log(self) -> str:
        """Vẽ bảng MQTT log."""
        lines = []
        header = self._color(Colors.WHITE, Colors.BG_GREEN, bold=True) + \
                 f"{'MQTT Events':^77}" + \
                 self._reset()
        lines.append(self._color(Colors.GREEN) + "+" + "-" * 77 + "+" + self._reset())
        lines.append(header)
        lines.append(self._color(Colors.GREEN) + "+" + "-" * 77 + "+" + self._reset())

        if not self._log_entries:
            lines.append(self._color(Colors.DIM) + f"|{'Waiting for MQTT events...':^77}|" + self._reset())
        else:
            for entry in self._log_entries:
                lines.append(entry)

        lines.append(self._color(Colors.GREEN) + "+" + "-" * 77 + "+" + self._reset())
        return "\n".join(lines)

    def _render_footer(self) -> str:
        """Vẽ footer với thông tin."""
        uptime = int(time.time() - self._start_time) if hasattr(self, '_start_time') else 0
        m, s = divmod(uptime, 60)
        h, m = divmod(m, 60)

        from . import config
        footer_text = (
            f"Broker: {config.MQTT_BROKER}:{config.MQTT_PORT}  |  "
            f"Client: {config.CLIENT_ID}  |  "
            f"Uptime: {h:02d}:{m:02d}:{s:02d}  |  "
            "Press Ctrl+C to exit"
        )
        return self._color(Colors.BLACK, Colors.BG_WHITE) + footer_text + self._reset()

    def render(self, state: Dict[str, bool]):
        """Render toàn bộ UI."""
        now = time.time()
        if now - self._last_render_time < self._render_interval:
            return
        self._last_render_time = now

        self._start_time = getattr(self, '_start_time', time.time())

        # Only clear if state changed
        if state != self._last_state:
            print("\033[2J\033[H", end="")  # Clear screen
            self._last_state = state.copy()

        lines = []

        lines.append(self._render_header())
        lines.append("")
        lines.append(self._render_relay_table(state))
        lines.append("")
        lines.append(self._render_action_log())
        lines.append("")
        lines.append(self._render_mqtt_log())
        lines.append("")
        lines.append(self._render_footer())

        print("\n".join(lines), flush=True)

    def log(self, message: str, level: str = "info"):
        """Thêm log entry."""
        ts = self._timestamp()

        color_map = {
            "info":    Colors.CYAN,
            "success": Colors.GREEN,
            "warning": Colors.YELLOW,
            "error":   Colors.RED,
            "mqtt_in": Colors.BRIGHT_CYAN,
            "mqtt_out": Colors.BRIGHT_MAGENTA,
        }
        color = color_map.get(level, Colors.WHITE)

        entry = f"|{self._color(Colors.YELLOW) + ts + self._reset()} {self._color(color) + message:^72}{self._reset()}|"
        self._log_entries.append(entry)

    def log_action(self, action: str, priority: str = "normal"):
        """Thêm action vào log."""
        self._action_entries.append({
            "time": self._timestamp(),
            "action": action,
            "priority": priority
        })

    def set_connected(self, connected: bool):
        """Cập nhật trạng thái kết nối."""
        if connected != self._connected:
            self._connected = connected
            if connected:
                self.log("MQTT connected to broker", "success")
            else:
                self.log("MQTT disconnected", "warning")

    def clear(self):
        """Xóa màn hình console."""
        print("\033[2J\033[H", end="")
