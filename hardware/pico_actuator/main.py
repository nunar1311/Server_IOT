# ============================================================
# AI-Guardian - Pico RP2040 Actuator Controller
# Nhan lenh tu MQTT, dieu khien relay/actuator
# ============================================================
#
# Kenh Relay (GP0-GP7):
#   CH1 (GP0)  -> CO2 Solenoid Valve
#   CH2 (GP1)  -> Water Pump
#   CH3 (GP2)  -> Exhaust Fan
#   CH4 (GP3)  -> Main Power Cutoff
#   CH5 (GP4)  -> UPS Switch
#   CH6 (GP5)  -> Buzzer/Alarm
#   CH7 (GP6)  -> Warning Light (Red)
#   CH8 (GP7)  -> Door Lock
#
# I2C (GP16=SDA, GP17=SCL) -> Giao tiep ESP32
# ============================================================

from machine import Pin, I2C, UART, PWM
import network
import ujson
import utime
import urandom
import sys
import os

try:
    from umqtt.simple import MQTTClient
except ImportError:
    MQTTClient = None

# ===================== CONFIGURATION =====================
MQTT_BROKER = "192.168.1.100"
MQTT_PORT    = 1883
MQTT_USER    = "mqtt_user"
MQTT_PASS    = "mqtt_password"
CLIENT_ID    = "pico_actuator_" + str(urandom.getrandbits(16))

MQTT_TOPIC_ACTIONS  = "ai-guardian/actions"
MQTT_TOPIC_STATUS   = "ai-guardian/actuator/status"
MQTT_TOPIC_ACK      = "ai-guardian/actuator/ack"

# ===================== RELAY PINS =====================
RELAY_PINS = [0, 1, 2, 3, 4, 5, 6, 7]
relays = {}
for p in RELAY_PINS:
    relays[p] = Pin(p, Pin.OUT)
    relays[p].value(0)

# Buzzer PWM
buzzer = PWM(Pin(15))
buzzer.duty_u16(0)

# Status LED
led = Pin(25, Pin.OUT)
led.value(0)

# ===================== I2C COMMUNICATION =====================
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
print("I2C devices found:", i2c.scan())

# ===================== STATE =====================
actuator_state = {
    "co2": False,
    "pump": False,
    "fan": False,
    "power_cut": False,
    "ups_switch": False,
    "buzzer": False,
    "warning_light": False,
    "door_lock": False,
    "last_action": None,
    "last_update": 0
}

# ===================== RELAY CONTROL =====================
RELAY_MAP = {
    "co2":           0,   # GP0 - CO2 Solenoid
    "pump":          1,   # GP1 - Water Pump
    "fan":           2,   # GP2 - Exhaust Fan
    "power_cut":     3,   # GP3 - Main Power Cutoff
    "ups_switch":    4,   # GP4 - UPS Switch
    "buzzer":        5,   # GP5 - Buzzer/Alarm
    "warning_light": 6,   # GP6 - Warning Light
    "door_lock":     7,   # GP7 - Door Lock
}

def activate_relay(channel, state):
    if channel in RELAY_PINS:
        relays[channel].value(1 if state else 0)
        return True
    return False

def set_actuator(name, state):
    ch = RELAY_MAP.get(name)
    if ch is not None:
        activate_relay(ch, state)
        actuator_state[name] = state
        actuator_state["last_action"] = name
        actuator_state["last_update"] = utime.time()
        print(f"Actuator '{name}' -> {'ON' if state else 'OFF'}")
        return True
    return False

def all_off():
    for name in RELAY_MAP:
        set_actuator(name, False)
    print("All actuators OFF")

# ===================== ALARM SEQUENCE =====================
def alarm_beep(pattern="emergency"):
    """Alarm beep patterns."""
    if pattern == "emergency":
        for _ in range(5):
            buzzer.duty_u16(20000)
            utime.sleep_ms(200)
            buzzer.duty_u16(0)
            utime.sleep_ms(200)
    elif pattern == "warning":
        for _ in range(3):
            buzzer.duty_u16(15000)
            utime.sleep_ms(500)
            buzzer.duty_u16(0)
            utime.sleep_ms(500)
    elif pattern == "ok":
        buzzer.duty_u16(10000)
        utime.sleep_ms(100)
        buzzer.duty_u16(0)
    buzzer.duty_u16(0)

# ===================== ACTION HANDLER =====================
def handle_action(data):
    """Handle incoming MQTT action commands."""
    action = data.get("action", "")
    priority = data.get("priority", "normal")

    print(f"Action: {action} (priority: {priority})")

    if action == "fire":
        set_actuator("buzzer", True)
        alarm_beep("emergency")
        set_actuator("warning_light", True)
        utime.sleep(0.5)
        set_actuator("co2", True)
        set_actuator("fan", True)
        if priority == "critical":
            set_actuator("power_cut", True)
        publish_ack("fire", "handled")

    elif action == "flood":
        set_actuator("buzzer", True)
        alarm_beep("warning")
        set_actuator("pump", True)
        set_actuator("warning_light", True)
        if priority == "critical":
            set_actuator("power_cut", True)
        publish_ack("flood", "handled")

    elif action == "gas_leak":
        set_actuator("buzzer", True)
        alarm_beep("emergency")
        set_actuator("fan", True)
        set_actuator("warning_light", True)
        if priority == "critical":
            set_actuator("power_cut", True)
        publish_ack("gas_leak", "handled")

    elif action == "electric_leak":
        set_actuator("buzzer", True)
        alarm_beep("emergency")
        set_actuator("warning_light", True)
        utime.sleep(0.3)
        set_actuator("power_cut", True)
        publish_ack("electric_leak", "handled")

    elif action == "intrusion":
        set_actuator("buzzer", True)
        alarm_beep("warning")
        set_actuator("warning_light", True)
        set_actuator("door_lock", True)
        publish_ack("intrusion", "handled")

    elif action == "temp_high":
        set_actuator("fan", True)
        if priority == "critical":
            set_actuator("buzzer", True)
            set_actuator("warning_light", True)
        publish_ack("temp_high", "handled")

    elif action == "clear":
        all_off()
        alarm_beep("ok")
        publish_ack("clear", "handled")

    elif action == "reset":
        all_off()
        publish_ack("reset", "handled")

    elif action == "manual":
        for key, val in data.get("devices", {}).items():
            set_actuator(key, bool(val))
        publish_ack("manual", "handled")

    else:
        print(f"Unknown action: {action}")

# ===================== MQTT =====================
mqtt_client = None

def setup_mqtt():
    global mqtt_client
    if MQTTClient is None:
        print("umqtt not available - running in standalone mode")
        return False

    try:
        mqtt_client = MQTTClient(CLIENT_ID, MQTT_BROKER, MQTT_PORT,
                                  MQTT_USER, MQTT_PASS)
        mqtt_client.set_callback(on_mqtt_message)
        mqtt_client.connect()
        mqtt_client.subscribe(MQTT_TOPIC_ACTIONS)
        print("MQTT connected")
        return True
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        return False

def on_mqtt_message(topic, msg):
    try:
        topic_str = topic.decode() if isinstance(topic, bytes) else str(topic)
        msg_str   = msg.decode() if isinstance(msg, bytes) else str(msg)
        print(f"MQTT << {topic_str}: {msg_str}")
        data = ujson.loads(msg_str)
        handle_action(data)
    except Exception as e:
        print(f"Error processing message: {e}")

def publish_ack(action, status):
    if mqtt_client:
        try:
            ack = ujson.dumps({
                "node": CLIENT_ID,
                "action": action,
                "status": status,
                "actuators": actuator_state.copy()
            })
            mqtt_client.publish(MQTT_TOPIC_ACK, ack)
        except Exception as e:
            print(f"Ack publish failed: {e}")

def publish_status():
    if mqtt_client:
        try:
            status = ujson.dumps({
                "node": CLIENT_ID,
                "state": actuator_state,
                "uptime": utime.time()
            })
            mqtt_client.publish(MQTT_TOPIC_STATUS, status)
        except:
            pass

# ===================== I2C SLAVE =====================
def i2c_slave_poll():
    """Poll I2C for commands from ESP32."""
    if 0x20 in i2c.scan():
        try:
            data = i2c.readfrom(0x20, 64)
            if len(data) > 0:
                print("I2C <<", data)
                cmd = data.decode('utf-8', 'ignore').strip('\x00')
                if cmd:
                    try:
                        action_data = ujson.loads(cmd)
                        handle_action(action_data)
                    except:
                        handle_action({"action": cmd.strip()})
        except:
            pass

# ===================== MAIN =====================
def main():
    print("=" * 50)
    print("AI-Guardian - Pico RP2040 Actuator Controller")
    print("=" * 50)

    mqtt_ok = setup_mqtt()

    # Startup sequence
    all_off()
    utime.sleep(1)
    alarm_beep("ok")

    last_status_publish = 0
    last_i2c_poll = 0

    while True:
        now = utime.time()

        if mqtt_ok and mqtt_client:
            try:
                mqtt_client.check_msg()
            except Exception as e:
                print(f"MQTT error: {e}")
                mqtt_ok = setup_mqtt()

        if now - last_i2c_poll >= 1:
            i2c_slave_poll()
            last_i2c_poll = now

        if now - last_status_publish >= 30:
            publish_status()
            last_status_publish = now

        led.toggle()
        utime.sleep(0.5)

if __name__ == "__main__":
    main()
