#ifndef CONFIG_H
#define CONFIG_H

// ============================================================
// AI-Guardian - ESP32 Configuration
// ============================================================

// --- WiFi ---
#define WIFI_SSID             "YOUR_WIFI_SSID"
#define WIFI_PASSWORD         "YOUR_WIFI_PASSWORD"

// --- MQTT ---
#define MQTT_SERVER           "192.168.1.100"
#define MQTT_PORT             1883
#define MQTT_CLIENT_ID         "esp32_sensor_node"
#define MQTT_USER             "mqtt_user"
#define MQTT_PASS             "mqtt_password"
#define MQTT_TOPIC_SENSORS     "ai-guardian/sensors"
#define MQTT_TOPIC_ACTIONS     "ai-guardian/actions"
#define MQTT_TOPIC_STATUS      "ai-guardian/status"

// --- Sensor Thresholds ---
#define TEMP_WARNING          45.0f
#define TEMP_CRITICAL         55.0f
#define HUM_WARNING           80.0f
#define DUST_WARNING          35.0f
#define GAS_WARNING           60.0f
#define CURRENT_LEAK_WARNING  5.0f

// --- Timing ---
#define SENSOR_READ_INTERVAL   30000   // ms
#define MQTT_RECONNECT_DELAY   5000    // ms
#define WEB_BROADCAST_INTERVAL 1000    // ms

// --- Hardware (ESP32 NodeMCU-32S) ---
#define LED_STATUS_PIN         2
#define DHT_PIN              32
#define DHTTYPE              DHT11  // Hoac DHT22 neu ban co
#define PIR_PIN              26
#define DOOR_PIN             27
#define LEAK_PIN             34    // INPUT ONLY
#define GAS_PIN              33
#define CURRENT_PIN          35    // INPUT ONLY
#define VOLTAGE_PIN_1      36    // INPUT ONLY - AC Input
#define VOLTAGE_PIN_2      39    // INPUT ONLY - UPS Voltage
#define PMS_RX               16    // UART2 RX
#define PMS_TX               17    // UART2 TX

// --- OTA ---
#define OTA_PASSWORD          "ai-guardian-ota"

// --- OLED 1.3" SH1106 I2C ---
#define OLED_SDA_PIN          21
#define OLED_SCL_PIN          22
#define OLED_I2C_ADDR         0x3C    // 0x3C hoac 0x3D
#define OLED_TEXT_SIZE        1
#define OLED_UPDATE_INTERVAL  3000    // ms (3 giay)
#define OLED_LED_PIN          4       // LED backlight (optional)

#endif // CONFIG_H
