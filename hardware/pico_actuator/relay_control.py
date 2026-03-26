# ============================================================
# AI-Guardian - Relay Control Module for Pico RP2040
# ============================================================

from machine import Pin

class RelayController:
    """8-channel relay controller for Pico RP2040."""

    RELAY_NAMES = [
        "co2",           # CH1 - CO2 Solenoid Valve
        "pump",           # CH2 - Water Pump
        "fan",            # CH3 - Exhaust Fan
        "power_cut",      # CH4 - Main Power Cutoff
        "ups_switch",     # CH5 - UPS Switch
        "buzzer",         # CH6 - Buzzer/Alarm
        "warning_light",  # CH7 - Warning Light
        "door_lock",      # CH8 - Door Lock
    ]

    def __init__(self, pins=None):
        if pins is None:
            pins = [0, 1, 2, 3, 4, 5, 6, 7]

        self._relays = {}
        self._state = {}

        for i, pin_num in enumerate(pins):
            name = self.RELAY_NAMES[i] if i < len(self.RELAY_NAMES) else f"ch{i+1}"
            self._relays[name] = Pin(pin_num, Pin.OUT)
            self._relays[name].value(0)
            self._state[name] = False

    def set(self, name, on):
        """Set relay state by name."""
        if name in self._relays:
            self._relays[name].value(1 if on else 0)
            self._state[name] = on
            return True
        return False

    def on(self, name):
        """Turn relay ON."""
        return self.set(name, True)

    def off(self, name):
        """Turn relay OFF."""
        return self.set(name, False)

    def toggle(self, name):
        """Toggle relay state."""
        if name in self._state:
            return self.set(name, not self._state[name])
        return False

    def all_off(self):
        """Turn all relays OFF."""
        for name in self._relays:
            self._relays[name].value(0)
            self._state[name] = False

    def all_on(self):
        """Turn all relays ON (use with caution)."""
        for name in self._relays:
            self._relays[name].value(1)
            self._state[name] = True

    def state(self, name):
        """Get relay state."""
        return self._state.get(name, None)

    def all_states(self):
        """Get all relay states."""
        return self._state.copy()

    def get_on_devices(self):
        """Return list of currently ON devices."""
        return [name for name, state in self._state.items() if state]

    def fire_emergency(self):
        self.off("buzzer")
        self.on("buzzer")
        self.on("warning_light")
        self.on("co2")
        self.on("fan")
        self.on("power_cut")

    def flood_response(self):
        self.on("pump")
        self.on("warning_light")
        self.on("buzzer")
        self.on("power_cut")

    def gas_leak_response(self):
        self.on("fan")
        self.on("warning_light")
        self.on("buzzer")
        self.on("power_cut")

    def intrusion_response(self):
        self.on("buzzer")
        self.on("warning_light")
        self.on("door_lock")
