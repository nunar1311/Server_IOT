# ============================================================
# AI-Guardian - Tkinter GUI for Pico Emulator
# Optional graphical user interface
# ============================================================

import threading
import time
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional, Dict, Callable

from . import config


class TkinterUI:
    """
    Tkinter GUI cho Pico Emulator.
    Optional - chạy song song với console UI.
    """

    def _create_style(self):
        """Tạo custom style cho widgets."""
        style = ttk.Style()

        # Configure colors
        style.configure("Title.TLabel",
                        foreground="#00BCD4",
                        font=("Consolas", 14, "bold"))

        style.configure("Status.TLabel",
                        font=("Consolas", 9))

        style.configure("Connected.TLabel",
                        foreground="#4CAF50",
                        font=("Consolas", 9, "bold"))

        style.configure("Disconnected.TLabel",
                        foreground="#F44336",
                        font=("Consolas", 9, "bold"))

        # Relay button styles
        style.configure("RelayOn.TButton",
                        background="#4CAF50",
                        foreground="#FFFFFF",
                        font=("Consolas", 8))

        style.configure("RelayOff.TButton",
                        background="#424242",
                        foreground="#BDBDBD",
                        font=("Consolas", 8))

        # Action button styles
        style.configure("Fire.TButton",
                        background="#F44336",
                        foreground="#FFFFFF",
                        font=("Consolas", 9, "bold"))

        style.configure("Flood.TButton",
                        background="#2196F3",
                        foreground="#FFFFFF",
                        font=("Consolas", 9, "bold"))

        style.configure("Gas.TButton",
                        background="#FF9800",
                        foreground="#000000",
                        font=("Consolas", 9, "bold"))

        style.configure("Electric.TButton",
                        background="#9C27B0",
                        foreground="#FFFFFF",
                        font=("Consolas", 9, "bold"))

        style.configure("Intrusion.TButton",
                        background="#00BCD4",
                        foreground="#000000",
                        font=("Consolas", 9, "bold"))

        style.configure("Clear.TButton",
                        background="#4CAF50",
                        foreground="#FFFFFF",
                        font=("Consolas", 9, "bold"))

        style.configure("Reset.TButton",
                        background="#607D8B",
                        foreground="#FFFFFF",
                        font=("Consolas", 9, "bold"))

        return style

    def __init__(self, on_relay_toggle: Optional[Callable] = None,
                 on_action: Optional[Callable] = None,
                 on_close: Optional[Callable] = None):
        self._on_relay_toggle = on_relay_toggle
        self._on_action = on_action
        self._on_close = on_close

        self._relay_buttons: Dict[str, ttk.Button] = {}
        self._relay_labels: Dict[str, tk.Label] = {}
        self._relay_frames: Dict[str, tk.Frame] = {}
        self._state: Dict[str, bool] = {name: False for name in config.RELAY_MAP}
        self._connected = False

        self._root: Optional[tk.Tk] = None
        self._log_widget: Optional[scrolledtext.ScrolledText] = None
        self._status_label: Optional[ttk.Label] = None
        self._uptime_label: Optional[ttk.Label] = None
        self._update_thread: Optional[threading.Thread] = None
        self._running = False

    def _create_widgets(self):
        """Tạo các widgets cho giao diện."""
        self._root.title("AI-Guardian Pico RP2040 Emulator")
        self._root.geometry("700x650")
        self._root.resizable(False, False)
        self._root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Main container
        main_frame = ttk.Frame(self._root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Title ---
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(title_frame,
                                text="AI-Guardian Pico RP2040 Emulator [WINDOWS]",
                                style="Title.TLabel")
        title_label.pack()

        # --- Status bar ---
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self._status_label = ttk.Label(status_frame,
                                       text="MQTT: DISCONNECTED",
                                       style="Disconnected.TLabel")
        self._status_label.pack(side=tk.LEFT)

        self._uptime_label = ttk.Label(status_frame,
                                       text="Uptime: 00:00:00",
                                       style="Status.TLabel")
        self._uptime_label.pack(side=tk.RIGHT)

        # --- Relay Grid (2 columns) ---
        relay_frame = ttk.LabelFrame(main_frame,
                                     text="Relay Status",
                                     padding=10)
        relay_frame.pack(fill=tk.X, pady=(0, 10))

        relay_names = list(config.RELAY_MAP.keys())
        half = (len(relay_names) + 1) // 2

        for i, name in enumerate(relay_names):
            row = i % half
            col = i // half

            frame = tk.Frame(relay_frame, padx=5, pady=5)
            frame.grid(row=row, column=col, sticky="ew", padx=5, pady=5)

            desc = config.RELAY_DESCRIPTIONS.get(name, name)
            gp = config.RELAY_MAP[name]

            # LED indicator
            led_canvas = tk.Canvas(frame, width=20, height=20)
            led_canvas.pack(side=tk.LEFT, padx=5)

            led_id = led_canvas.create_oval(3, 3, 18, 18,
                                            fill="#424242",
                                            outline="#616161")
            self._relay_frames[name] = led_canvas
            self._relay_frames[f"{name}_led"] = led_id

            # Label
            label = ttk.Label(frame,
                              text=f"GP{gp} {desc}",
                              font=("Consolas", 8))
            label.pack(side=tk.LEFT, padx=5)

            # Button
            btn = ttk.Button(frame,
                             text="OFF",
                             width=6,
                             command=lambda n=name: self._toggle_relay(n))
            btn.pack(side=tk.RIGHT)
            self._relay_buttons[name] = btn

        # Configure grid weights
        relay_frame.columnconfigure(0, weight=1)
        relay_frame.columnconfigure(1, weight=1)

        # --- Action Buttons ---
        action_frame = ttk.LabelFrame(main_frame,
                                      text="Emergency Actions",
                                      padding=10)
        action_frame.pack(fill=tk.X, pady=(0, 10))

        actions_row1 = [
            ("FIRE", "fire", "Fire.TButton"),
            ("FLOOD", "flood", "Flood.TButton"),
            ("GAS LEAK", "gas_leak", "Gas.TButton"),
            ("ELECTRIC", "electric_leak", "Electric.TButton"),
        ]

        actions_row2 = [
            ("INTRUSION", "intrusion", "Intrusion.TButton"),
            ("TEMP HIGH", "temp_high", "Gas.TButton"),
            ("CLEAR", "clear", "Clear.TButton"),
            ("RESET", "reset", "Reset.TButton"),
        ]

        for i, (text, action, style) in enumerate(actions_row1):
            btn = ttk.Button(action_frame,
                             text=text,
                             style=style,
                             command=lambda a=action: self._trigger_action(a))
            btn.grid(row=0, column=i, padx=3, pady=3, sticky="ew")

        for i, (text, action, style) in enumerate(actions_row2):
            btn = ttk.Button(action_frame,
                             text=text,
                             style=style,
                             command=lambda a=action: self._trigger_action(a))
            btn.grid(row=1, column=i, padx=3, pady=3, sticky="ew")

        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)
        action_frame.columnconfigure(2, weight=1)
        action_frame.columnconfigure(3, weight=1)

        # --- Manual Control ---
        manual_frame = ttk.LabelFrame(main_frame,
                                      text="Manual Control",
                                      padding=10)
        manual_frame.pack(fill=tk.X, pady=(0, 10))

        for i, name in enumerate(relay_names[:4]):
            desc = config.RELAY_DESCRIPTIONS.get(name, name)
            btn = ttk.Button(manual_frame,
                             text=f"{desc} [OFF]",
                             width=18,
                             command=lambda n=name: self._toggle_relay(n))
            btn.grid(row=0, column=i, padx=3, pady=3)
            self._relay_buttons[f"manual_{name}"] = btn

        for i, name in enumerate(relay_names[4:]):
            desc = config.RELAY_DESCRIPTIONS.get(name, name)
            btn = ttk.Button(manual_frame,
                             text=f"{desc} [OFF]",
                             width=18,
                             command=lambda n=name: self._toggle_relay(n))
            btn.grid(row=1, column=i, padx=3, pady=3)
            self._relay_buttons[f"manual_{name}"] = btn

        manual_frame.columnconfigure(0, weight=1)
        manual_frame.columnconfigure(1, weight=1)
        manual_frame.columnconfigure(2, weight=1)
        manual_frame.columnconfigure(3, weight=1)

        # --- Log Window ---
        log_frame = ttk.LabelFrame(main_frame,
                                   text="Event Log",
                                   padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self._log_widget = scrolledtext.ScrolledText(
            log_frame,
            height=8,
            font=("Consolas", 8),
            state=tk.DISABLED,
            bg="#1E1E1E",
            fg="#00FF00"
        )
        self._log_widget.pack(fill=tk.BOTH, expand=True)

    def _toggle_relay(self, name: str):
        """Toggle relay state."""
        if self._on_relay_toggle:
            current = self._state.get(name, False)
            self._on_relay_toggle(name, not current)

    def _trigger_action(self, action: str):
        """Trigger action."""
        if self._on_action:
            self._on_action(action, "normal")
            self._add_log(f"Action triggered: {action.upper()}")

    def _update_relay_ui(self, name: str, state: bool):
        """Cập nhật UI cho relay."""
        if name not in self._relay_frames:
            return

        led_id = self._relay_frames.get(f"{name}_led")
        canvas = self._relay_frames.get(name)

        if led_id and canvas:
            color = "#4CAF50" if state else "#424242"
            canvas.itemconfig(led_id, fill=color)

        if name in self._relay_buttons:
            text = "ON" if state else "OFF"
            self._relay_buttons[name].config(text=text)

        manual_key = f"manual_{name}"
        if manual_key in self._relay_buttons:
            desc = config.RELAY_DESCRIPTIONS.get(name, name)
            text = f"{desc} [{'ON' if state else 'OFF'}]"
            self._relay_buttons[manual_key].config(text=text)

    def update_state(self, state: Dict[str, bool]):
        """Cập nhật trạng thái relay."""
        for name, s in state.items():
            if name in self._state:
                if self._state[name] != s:
                    self._state[name] = s
                    self._update_relay_ui(name, s)

    def set_connected(self, connected: bool):
        """Cập nhật trạng thái kết nối MQTT."""
        self._connected = connected
        if self._status_label:
            if connected:
                self._status_label.config(text="MQTT: CONNECTED",
                                          style="Connected.TLabel")
            else:
                self._status_label.config(text="MQTT: DISCONNECTED",
                                          style="Disconnected.TLabel")

    def _update_uptime(self):
        """Cập nhật uptime."""
        if hasattr(self, '_start_time'):
            uptime = int(time.time() - self._start_time)
            m, s = divmod(uptime, 60)
            h, m = divmod(m, 60)
            if self._uptime_label:
                self._uptime_label.config(text=f"Uptime: {h:02d}:{m:02d}:{s:02d}")

    def _add_log(self, message: str):
        """Thêm log entry."""
        if self._log_widget:
            ts = time.strftime("%H:%M:%S")
            self._log_widget.config(state=tk.NORMAL)
            self._log_widget.insert(tk.END, f"[{ts}] {message}\n")
            self._log_widget.see(tk.END)
            self._log_widget.config(state=tk.DISABLED)

    def _update_loop(self):
        """Background update loop."""
        while self._running:
            self._update_uptime()
            time.sleep(1)

    def _on_window_close(self):
        """Xử lý khi đóng cửa sổ."""
        if self._on_close:
            self._on_close()
        self.stop()

    def start(self):
        """Khởi động GUI."""
        self._root = tk.Tk()
        self._create_style()
        self._create_widgets()
        self._start_time = time.time()
        self._running = True
        self._update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self._update_thread.start()
        self._add_log("Pico Emulator GUI started")
        self._root.mainloop()

    def stop(self):
        """Dừng GUI."""
        self._running = False
        if self._root:
            self._root.quit()
