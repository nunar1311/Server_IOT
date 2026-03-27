# ============================================================
# AI-Guardian - Sound Manager for Pico Emulator
# Buzzer sound simulation using Windows winsound
# ============================================================

import threading
import time
from typing import Optional

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

from . import config


class SoundManager:
    """
    Quản lý âm thanh buzzer trên Windows.
    Sử dụng winsound (native Windows) hoặc threading fallback.
    """

    def __init__(self, enabled: bool = True):
        self._enabled = enabled
        self._playing = False
        self._thread: Optional[threading.Thread] = None

    def _play_beep_async(self, frequency: int, duration_ms: int):
        """Phát beep không đồng bộ."""
        if not self._enabled:
            return

        if HAS_WINSOUND:
            try:
                winsound.Beep(frequency, duration_ms)
            except Exception:
                pass
        else:
            time.sleep(duration_ms / 1000.0)

    def play_pattern(self, pattern_name: str):
        """
        Phát pattern âm thanh.
        pattern_name: "emergency", "warning", "ok"
        """
        if not self._enabled:
            return

        pattern = config.BUZZER_PATTERNS.get(pattern_name)
        if not pattern:
            return

        if self._thread and self._thread.is_alive():
            return

        self._thread = threading.Thread(
            target=self._play_pattern_thread,
            args=(pattern,),
            daemon=True
        )
        self._thread.start()

    def _play_pattern_thread(self, pattern):
        """Thread worker để phát pattern."""
        for frequency, duration_ms in pattern:
            if frequency == 0:
                time.sleep(duration_ms / 1000.0)
            else:
                self._play_beep_async(frequency, duration_ms)

    def play_emergency(self):
        """Phát âm emergency (5x beep nhanh)."""
        self.play_pattern("emergency")

    def play_warning(self):
        """Phát âm warning (3x beep vua)."""
        self.play_pattern("warning")

    def play_ok(self):
        """Phát âm OK (1x beep ngan)."""
        self.play_pattern("ok")

    def stop(self):
        """Dừng phát âm thanh."""
        self._playing = False

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
