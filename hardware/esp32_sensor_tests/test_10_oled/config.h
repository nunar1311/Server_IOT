// ============================================================
// CAU HINH CHUNG - TEST CAM BIEN ESP32 NodeMCU-32S
// ============================================================
// Chu y: Chi can thay doi cau hinh o day de phu hop voi board
// ============================================================

#ifndef CONFIG_H
#define CONFIG_H

// ========== WIFI ==========
#define WIFI_SSID "Hoang Quan"
#define WIFI_PASSWORD "hoangquan@@"

// ========== MQTT ==========
#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
#define MQTT_USER "mqtt_user"
#define MQTT_PASSWORD "mqtt_password"
#define MQTT_CLIENT_ID "ESP32_Sensor_Test"
#define MQTT_TOPIC "test/sensor"

// ========== SERIAL DEBUG ==========
#define SERIAL_BAUD 115200

// ========== GPIO PINS ==========
// --- DHT11 (Nhiet do / Do am) ---
#define DHT_PIN 32
#define DHT_TYPE DHT11

// --- PMS5003 (Bu PM2.5) ---
#define PMS_TX_PIN 17
#define PMS_RX_PIN 16

// --- MQ-2 (Khoi / Gas) ---
#define MQ2_PIN 33
#define MQ2_ANA_PIN 33
#define MQ2_D0_PIN 4
#define RL_VALUE 5.0
#define RO_CLEAN_AIR_FACTOR 9.83

// --- Leak Sensor (Ro nuoc) ---
#define LEAK_PIN 34
#define LEAK_LED_PIN 2

// --- ACS712 (Ro dien 30A) ---
#define ACS712_PIN 35
#define ACS712_SENSITIVITY 0.066  // 30A model: 66mV/A
#define ACS712_VCC 3.3

// --- HC-SR501 (Chuyen dong) ---
#define PIR_PIN 26
#define PIR_LED_PIN 25

// --- Reed Switch (Cua mo) ---
#define REED_PIN 27
#define REED_LED_PIN 33

// --- Voltage Divider AC ---
#define AC_VOLTAGE_PIN 36
#define AC_R1 100000.0
#define AC_R2 10000.0
#define AC_CALIBRATION 1.0

// --- Voltage Divider UPS ---
#define UPS_VOLTAGE_PIN 39
#define UPS_R1 100000.0
#define UPS_R2 10000.0
#define UPS_CALIBRATION 1.0

// --- OLED 1.3" SH1106 I2C ---
#define OLED_SDA_PIN 21
#define OLED_SCL_PIN 22
#define OLED_I2C_ADDR 0x3C
#define OLED_TEXT_SIZE 1
#define OLED_LED_PIN 4

// ========== ADC SETTINGS ==========
#define ADC_ATTEN ADC_ATTEN_DB_11    // 0-3.3V
#define ADC_WIDTH ADC_WIDTH_BIT_12   // 12-bit

// ========== NGƯỠNG CẢNH BÁO ==========
#define TEMP_MAX 45.0
#define TEMP_MIN 10.0
#define HUMIDITY_MAX 95.0
#define HUMIDITY_MIN 20.0
#define PM25_MAX 35.0
#define GAS_THRESHOLD 300
#define AC_VOLTAGE_MIN 200.0
#define AC_VOLTAGE_MAX 250.0
#define UPS_VOLTAGE_MIN 11.0
#define UPS_VOLTAGE_MAX 13.8

// ========== TIMING ==========
#define DHT_READ_INTERVAL 2000       // ms
#define PMS_READ_INTERVAL 1000       // ms
#define MQ2_READ_INTERVAL 500        // ms
#define OLED_UPDATE_INTERVAL 1000    // ms

#endif
