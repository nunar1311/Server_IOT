# ============================================================
# AI-Guardian - I2C Communication Module for Pico RP2040
# Giao tiep I2C voi ESP32
# ============================================================

from machine import I2C, Pin

class I2CComm:
    """
    I2C Communication handler between Pico RP2040 and ESP32.
    ESP32 acts as I2C master (address 0x20), Pico as slave.
    """

    ESP32_I2C_ADDR = 0x20

    def __init__(self, i2c_obj=None, sda=16, scl=17, freq=400000):
        if i2c_obj:
            self._i2c = i2c_obj
        else:
            self._i2c = I2C(0, sda=Pin(sda), scl=Pin(scl), freq=freq)

    def scan(self):
        """Scan I2C bus for devices."""
        return self._i2c.scan()

    def send_command(self, command, data=None):
        """Send command to ESP32 master."""
        msg = {"cmd": command}
        if data:
            msg.update(data)
        import ujson
        payload = ujson.dumps(msg)
        try:
            self._i2c.writeto(self.ESP32_I2C_ADDR, payload.encode())
            return True
        except Exception as e:
            print(f"I2C send error: {e}")
            return False

    def receive_data(self, num_bytes=64):
        """Receive data from ESP32 master."""
        try:
            devices = self.scan()
            if self.ESP32_I2C_ADDR in devices:
                data = self._i2c.readfrom(self.ESP32_I2C_ADDR, num_bytes)
                return data.decode('utf-8', 'ignore').strip('\x00')
        except Exception as e:
            print(f"I2C receive error: {e}")
        return None

    def parse_sensor_data(self, raw_data):
        """Parse incoming sensor data from ESP32."""
        import ujson
        try:
            return ujson.loads(raw_data)
        except:
            return None

    def ping(self):
        """Ping ESP32 to check connection."""
        return self.send_command("ping")

    def request_status(self):
        """Request status from ESP32."""
        return self.send_command("status")
