# ============================================================
# AI-Guardian - Pico RP2040 Emulator for Windows
# Entry point - main.py
# ============================================================
#
# Usage:
#   python main.py                          # Console UI (default)
#   python main.py --gui                    # Tkinter GUI
#   python main.py --broker 192.168.1.100 # Custom broker
#   python main.py --port 1883             # Custom port
#   python main.py --no-sound              # Disable buzzer sounds
#   python main.py --console               # Force console UI
#
# Build Windows EXE:
#   pyinstaller --onefile --name PicoEmulator main.py
# ============================================================

import sys
import os
import time
import signal
import argparse
import threading
from typing import Optional

# Add parent directory to path so we can import pico_emulator package
_EMULATOR_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_DIR = os.path.dirname(_EMULATOR_DIR)
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)

from pico_emulator import config
from pico_emulator.emulator_core import PicoEmulatorCore
from pico_emulator.mqtt_client import PicoMQTTClient
from pico_emulator.sound_manager import SoundManager
from pico_emulator.ui_console import ConsoleUI
from pico_emulator.ui_tkinter import TkinterUI


class PicoEmulatorApp:
    """
    Main application class cho Pico Emulator.
    Orchestrates core, MQTT, sound, and UI components.
    """

    def __init__(self, use_gui: bool = False, no_sound: bool = False,
                 broker: Optional[str] = None, port: Optional[int] = None):
        self._use_gui = use_gui
        self._running = False
        self._started = False
        self._shutdown_event = threading.Event()

        # Override config if provided
        if broker:
            config.MQTT_BROKER = broker
        if port:
            config.MQTT_PORT = port

        # Init components
        self._sound = SoundManager(enabled=not no_sound)

        # Callbacks for core
        def on_state_change(name, state, old_state):
            msg = f"RELAY {name:15} -> {'ON ' if state else 'OFF'}"
            if hasattr(self, '_console'):
                self._console.log(msg, "success" if state else "warning")

        def on_action(action, priority):
            if hasattr(self, '_console'):
                self._console.log_action(action, priority)

        def on_alarm(pattern):
            if pattern == "emergency":
                self._sound.play_emergency()
            elif pattern == "warning":
                self._sound.play_warning()
            elif pattern == "ok":
                self._sound.play_ok()

        self._core = PicoEmulatorCore(
            on_state_change=on_state_change,
            on_action=on_action,
            on_alarm=on_alarm
        )

        # MQTT callbacks
        def on_mqtt_connect():
            if hasattr(self, '_console'):
                self._console.set_connected(True)
            if hasattr(self, '_gui'):
                self._gui.set_connected(True)
            if hasattr(self, '_console'):
                self._console.log(f"Connected to {config.MQTT_BROKER}:{config.MQTT_PORT}", "success")

        def on_mqtt_disconnect(rc):
            if hasattr(self, '_console'):
                self._console.set_connected(False)
            if hasattr(self, '_gui'):
                self._gui.set_connected(False)
            if hasattr(self, '_console'):
                self._console.log(f"Disconnected (rc={rc})", "warning")

        def on_mqtt_message(topic, data):
            if hasattr(self, '_console'):
                self._console.log(f"MQTT << {topic}: {data.get('action', '')}", "mqtt_in")

        self._mqtt = PicoMQTTClient(
            core=self._core,
            on_connect=on_mqtt_connect,
            on_disconnect=on_mqtt_disconnect,
            on_message=on_mqtt_message
        )

        # UI
        self._console: Optional[ConsoleUI] = None
        self._gui: Optional[TkinterUI] = None

    def _init_console_ui(self):
        """Init console UI."""
        self._console = ConsoleUI()

        def on_relay_toggle(name, state):
            self._core.set_actuator(name, state)

        def on_action_trigger(action, priority):
            self._mqtt.publish_action(action, priority)

        self._console._on_relay_toggle = on_relay_toggle
        self._console._on_action_trigger = on_action_trigger

    def _init_gui_ui(self):
        """Init Tkinter GUI."""
        self._gui = TkinterUI(
            on_relay_toggle=lambda n, s: self._core.set_actuator(n, s),
            on_action=lambda a, p: self._mqtt.publish_action(a, p),
            on_close=self.shutdown
        )

    def _mqtt_publish_action(self, action: str, priority: str = "normal"):
        """Publish action to MQTT (called by UI)."""
        self._core.handle_action(action, priority)
        self._mqtt.publish_ack(action, "handled")

    def _console_input_loop(self):
        """Console input handling in separate thread."""
        print("\nConsole Commands:")
        print("  fire, flood, gas_leak, electric_leak, intrusion, temp_high, clear, reset")
        print("  manual <device> <on|off>  - Manual control")
        print("  status                        - Show status")
        print("  sound on|off                 - Toggle sound")
        print("  exit, quit                    - Exit")
        print()

        while self._running:
            try:
                cmd = input("> ").strip().lower()
                if not cmd:
                    continue

                if cmd in ("fire", "flood", "gas_leak", "electric_leak",
                           "intrusion", "temp_high", "clear", "reset"):
                    self._mqtt_publish_action(cmd, "normal")
                    if self._console:
                        self._console.log_action(cmd, "normal")
                        self._console.log(f"Action: {cmd}", "success")

                elif cmd.startswith("manual "):
                    parts = cmd.split()
                    if len(parts) == 3 and parts[1] in config.RELAY_MAP:
                        state = parts[2] == "on"
                        self._core.set_actuator(parts[1], state)
                        if self._console:
                            self._console.log(f"Manual: {parts[1]} = {'ON' if state else 'OFF'}", "info")

                elif cmd == "status":
                    state = self._core.get_state()
                    on_devices = self._core.get_on_devices()
                    print(f"  Status: {state}")
                    print(f"  ON devices: {on_devices}")

                elif cmd == "sound on":
                    self._sound.enabled = True
                    print("  Sound enabled")

                elif cmd == "sound off":
                    self._sound.enabled = False
                    print("  Sound disabled")

                elif cmd in ("exit", "quit", "q"):
                    self.shutdown()
                    break

            except (EOFError, KeyboardInterrupt):
                self.shutdown()
                break
            except Exception as e:
                if self._running:
                    print(f"Error: {e}")

    def _console_render_loop(self):
        """Console render loop in separate thread."""
        while self._running:
            if self._console:
                self._console.render(self._core.get_state())

            # Publish status periodically
            if self._mqtt.should_publish_status() and self._mqtt.is_connected():
                self._mqtt.publish_status()

            time.sleep(0.5)

    def _publish_action(self, action: str, priority: str = "normal"):
        """Publish action to MQTT (for GUI callbacks)."""
        self._core.handle_action(action, priority)
        self._mqtt.publish_ack(action, "handled")

    def start(self):
        """Start the emulator."""
        self._running = True

        # Print banner
        print("=" * 60)
        print("  AI-Guardian Pico RP2040 Emulator for Windows")
        print("  MQTT Broker: {}:{}".format(config.MQTT_BROKER, config.MQTT_PORT))
        print("  Client ID: {}".format(config.CLIENT_ID))
        print("  Mode: {}".format("GUI (Tkinter)" if self._use_gui else "Console"))
        print("  Sound: {}".format("Disabled" if not self._sound.enabled else "Enabled"))
        print("=" * 60)
        print()

        # Connect MQTT
        print(f"Connecting to MQTT broker {config.MQTT_BROKER}:{config.MQTT_PORT}...")
        if self._mqtt.connect():
            print("MQTT connection initiated")
        else:
            print("WARNING: MQTT connection failed. Will retry...")

        # Start console UI
        if not self._use_gui:
            self._init_console_ui()

            # Start console render loop
            render_thread = threading.Thread(target=self._console_render_loop, daemon=True)
            render_thread.start()

            # Start console input loop (blocking)
            self._console_input_loop()
        else:
            # Start GUI
            self._init_gui_ui()
            self._gui.start()

    def shutdown(self):
        """Graceful shutdown."""
        if not self._running:
            return

        print("\nShutting down...")
        self._running = False

        # Stop MQTT
        self._mqtt.disconnect()

        # Stop sound
        self._sound.stop()

        # Stop GUI
        if self._gui:
            self._gui.stop()

        self._shutdown_event.set()
        print("Shutdown complete.")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="AI-Guardian Pico RP2040 Emulator for Windows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                        # Console UI
  python main.py --gui                  # GUI mode
  python main.py --broker 192.168.1.100 # Custom broker
  python main.py --no-sound             # Disable sound
        """
    )

    parser.add_argument(
        "--gui", action="store_true",
        help="Use Tkinter GUI instead of console"
    )

    parser.add_argument(
        "--console", action="store_true",
        help="Force console UI (default)"
    )

    parser.add_argument(
        "--broker",
        help="MQTT broker address (default: localhost)"
    )

    parser.add_argument(
        "--port", type=int,
        help="MQTT broker port (default: 1883)"
    )

    parser.add_argument(
        "--no-sound", action="store_true",
        help="Disable buzzer sounds"
    )

    parser.add_argument(
        "--client-id",
        help="Custom client ID"
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Override client ID if provided
    if args.client_id:
        config.CLIENT_ID = args.client_id

    # Create and start app
    app = PicoEmulatorApp(
        use_gui=args.gui,
        no_sound=args.no_sound,
        broker=args.broker,
        port=args.port
    )

    # Handle Ctrl+C
    def signal_handler(sig, frame):
        app.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        app.start()
    except KeyboardInterrupt:
        app.shutdown()


if __name__ == "__main__":
    main()
