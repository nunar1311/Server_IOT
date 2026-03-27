# ============================================================
# AI-Guardian - Pico RP2040 Emulator Configuration
# ============================================================

# MQTT Connection
MQTT_BROKER = "localhost"
MQTT_PORT   = 1883
MQTT_USER   = "mqtt_user"
MQTT_PASS   = "mqtt_password"
CLIENT_ID   = "pico_emulator_win"

# MQTT Topics (same as Pico RP2040)
MQTT_TOPIC_ACTIONS = "ai-guardian/actions"
MQTT_TOPIC_STATUS  = "ai-guardian/actuator/status"
MQTT_TOPIC_ACK     = "ai-guardian/actuator/ack"

# Relay Mapping (GP0-GP7 on Pico, simulated here)
RELAY_MAP = {
    "co2":            0,  # GP0 - CO2 Solenoid Valve
    "pump":           1,  # GP1 - Water Pump
    "fan":            2,  # GP2 - Exhaust Fan
    "power_cut":      3,  # GP3 - Main Power Cutoff
    "ups_switch":     4,  # GP4 - UPS Switch
    "buzzer":         5,  # GP5 - Buzzer/Alarm
    "warning_light":  6,  # GP6 - Warning Light
    "door_lock":      7,  # GP7 - Door Lock
}

RELAY_DESCRIPTIONS = {
    "co2":            "CO2 Solenoid Valve",
    "pump":           "Water Pump",
    "fan":            "Exhaust Fan",
    "power_cut":      "Main Power Cutoff",
    "ups_switch":     "UPS Switch",
    "buzzer":         "Buzzer/Alarm",
    "warning_light":  "Warning Light",
    "door_lock":      "Door Lock",
}

# Buzzer patterns (frequency Hz, duration ms)
BUZZER_PATTERNS = {
    "emergency": [(2000, 200), (0, 200)] * 5,
    "warning":   [(1500, 500), (0, 500)] * 3,
    "ok":        [(1000, 100)],
}

# Status publish interval (seconds)
STATUS_INTERVAL = 30

# I2C (simulated - not used in Windows emulator)
I2C_SDA = 16
I2C_SCL = 17
I2C_FREQ = 400000
