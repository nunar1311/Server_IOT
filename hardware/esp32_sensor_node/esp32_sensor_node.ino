# ============================================================
# AI-Guardian - ESP32 Sensor Node
# Thu thap du lieu cam bien, gui qua MQTT
# ============================================================
#
# Cam bien ket noi:
#   - DHT11 (Temp/Humidity)       -> IO32 (3.3V, 10K pull-up)
#   - PMS5003 (Dust/PM2.5)       -> UART2 (TX=IO17, RX=IO16), Baud 9600
#   - MQ-2 (Smoke/Gas)           -> IO33 (Analog)
#   - Leak Sensor                -> IO34 (Digital, INPUT ONLY, Active LOW)
#   - AC Current Sensor (ACS712) -> IO35 (Analog, INPUT ONLY)
#   - PIR HC-SR501 (Motion)      -> IO26 (Digital)
#   - Reed Switch (Door)         -> IO27 (Digital, Pull-up)
#   - Voltage Divider (UPS)      -> IO36, IO39 (Analog, INPUT ONLY)
#   - I2C (Pico + OLED)          -> IO21 (SDA), IO22 (SCL)
#   - OLED 1.3" SH1106           -> I2C (addr 0x3C), hien thi du lieu sensor
#
# Ho tro OTA Update
# ============================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <HardwareSerial.h>
#include <ArduinoJson.h>
#include <ESPAsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <AsyncWebSocket.h>
#include <ArduinoOTA.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "config.h"
#include "oled.h"

// ===================== CONFIGURATION =====================
#define WIFI_SSID             "YOUR_WIFI_SSID"
#define WIFI_PASSWORD         "YOUR_WIFI_PASSWORD"

#define MQTT_SERVER           "192.168.1.100"
#define MQTT_PORT             1883
#define MQTT_CLIENT_ID         "esp32_sensor_node"
#define MQTT_TOPIC_SENSORS     "ai-guardian/sensors"
#define MQTT_TOPIC_ACTIONS     "ai-guardian/actions"
#define MQTT_TOPIC_STATUS      "ai-guardian/status"

// ===================== HARDWARE PINS =====================
#define DHT_PIN               32
#define DHTTYPE               DHT11  // DHT11 (neu co DHT22 thi doi thanh DHT22)

#define PIR_PIN               26
#define DOOR_PIN              27
#define LEAK_PIN               34
#define GAS_PIN                33
#define CURRENT_PIN            35
#define VOLTAGE_PIN_1          36
#define VOLTAGE_PIN_2          39

// PMS5003 Dust Sensor - UART2 (IO16=RX, IO17=TX)
#define PMS_RX                16
#define PMS_TX                17

// LED Status
#define LED_STATUS_PIN         2

// ===================== OBJECTS =====================
DHT dht(DHT_PIN, DHTTYPE);
HardwareSerial pmsSerial(2);  // UART2

WiFiClient espClient;
PubSubClient mqttClient(espClient);

AsyncWebServer server(80);
AsyncWebSocket wsSensorData("/ws");

// ===================== STATE =====================
unsigned long lastReadingsTime = 0;
unsigned long lastMqttReconnect = 0;
unsigned long lastWebsocketBroadcast = 0;
const unsigned long READINGS_INTERVAL = 30000;   // 30 seconds
const unsigned long WEBSOCKET_INTERVAL = 1000;   // 1 second

bool sensorValuesUpdated = false;

// ===================== STRUCTURES =====================
struct SensorData {
    float temperature;
    float humidity;
    float dustPm25;
    float dustPm10;
    float gasLevel;
    bool  motionDetected;
    bool  doorOpen;
    bool  leakDetected;
    float currentLeak;
    float voltageInput;
    float voltageUps;
    unsigned long timestamp;
};

SensorData currentData;

// ===================== SETUP =====================
void setup() {
    Serial.begin(115200);
    pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);

    pinMode(LED_STATUS_PIN, OUTPUT);
    pinMode(PIR_PIN, INPUT);
    pinMode(DOOR_PIN, INPUT_PULLUP);
    pinMode(LEAK_PIN, INPUT_PULLUP);

    digitalWrite(LED_STATUS_PIN, LOW);

    dht.begin();

    initWiFi();
    initMQTT();
    initOTA();
    initWebSocket();
    initWebServer();
    initOLED();

    blinkLed(3);
}

// ===================== WIFI =====================
void initWiFi() {
    Serial.print("Connecting to WiFi: ");
    Serial.println(WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println();
        Serial.println("WiFi connected. IP: " + WiFi.localIP().toString());
        digitalWrite(LED_STATUS_PIN, HIGH);
    } else {
        Serial.println("WiFi FAILED - starting AP mode");
        WiFi.mode(WIFI_AP_STA);
        WiFi.softAP("AI-Guardian-Setup", "12345678");
        Serial.println("AP IP: " + WiFi.softAPIP().toString());
    }
}

// ===================== MQTT =====================
void initMQTT() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    mqttClient.setBufferSize(512);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    StaticJsonDocument<256> doc;
    DeserializationError error = deserializeJson(doc, payload, length);
    if (error) {
        Serial.println("MQTT parse error");
        return;
    }

    String t = String(topic);
    Serial.println("MQTT received on: " + t);

    if (t == MQTT_TOPIC_ACTIONS) {
        handleAction(doc.as<JsonObject>());
    }
}

void handleAction(JsonObject action) {
    const char* act = action["action"];
    Serial.print("Action received: ");
    Serial.println(act);

    if (strcmp(act, "reset") == 0) {
        ESP.restart();
    }
}

bool reconnectMQTT() {
    if (mqttClient.connected()) return true;

    Serial.print("Attempting MQTT connection...");
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
        Serial.println("connected");
        mqttClient.subscribe(MQTT_TOPIC_ACTIONS);
        publishStatus("online");
        return true;
    }
    Serial.print("failed, rc=");
    Serial.println(mqttClient.state());
    return false;
}

void publishStatus(const char* status) {
    StaticJsonDocument<128> doc;
    doc["node"] = MQTT_CLIENT_ID;
    doc["status"] = status;
    doc["rssi"] = WiFi.RSSI();
    doc["uptime"] = millis() / 1000;

    char buffer[128];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_STATUS, buffer);
}

// ===================== WEB SERVER =====================
void initWebServer() {
    server.on("/", HTTP_GET, [](AsyncWebServerRequest* request) {
        request->send(200, "text/plain", "AI-Guardian ESP32 Sensor Node\n/mqtt/status | /sensor/data | /ota/update");
    });

    server.on("/sensor/data", HTTP_GET, [](AsyncWebServerRequest* request) {
        StaticJsonDocument<512> doc;
        doc["temperature"] = currentData.temperature;
        doc["humidity"] = currentData.humidity;
        doc["dust_pm25"] = currentData.dustPm25;
        doc["dust_pm10"] = currentData.dustPm10;
        doc["gas"] = currentData.gasLevel;
        doc["motion"] = currentData.motionDetected;
        doc["door"] = currentData.doorOpen;
        doc["leak"] = currentData.leakDetected;
        doc["current_leak"] = currentData.currentLeak;
        doc["voltage_input"] = currentData.voltageInput;
        doc["voltage_ups"] = currentData.voltageUps;
        doc["rssi"] = WiFi.RSSI();
        doc["uptime"] = millis() / 1000;
        doc["ip"] = WiFi.localIP().toString();

        String response;
        serializeJson(doc, response);
        request->send(200, "application/json", response);
    });

    server.begin();
}

void initWebSocket() {
    wsSensorData.onEvent([](AsyncWebSocket* server, AsyncWebSocketClient* client,
                            AwsEventType type, void* arg, uint8_t* data, size_t len) {
        if (type == WS_EVT_CONNECT) {
            Serial.println("WebSocket client connected");
            client->text("{\"type\":\"connected\",\"node\":\"esp32_sensor\"}");
        }
    });
    server.addHandler(&wsSensorData);
}

void broadcastSensorData() {
    StaticJsonDocument<512> doc;
    doc["type"] = "sensor_update";
    doc["temperature"] = currentData.temperature;
    doc["humidity"] = currentData.humidity;
    doc["dust_pm25"] = currentData.dustPm25;
    doc["gas"] = currentData.gasLevel;
    doc["motion"] = currentData.motionDetected;
    doc["door"] = currentData.doorOpen;
    doc["leak"] = currentData.leakDetected;
    doc["rssi"] = WiFi.RSSI();
    doc["ts"] = millis();

    String output;
    serializeJson(doc, output);
    wsSensorData.textAll(output);
}

// ===================== OTA =====================
void initOTA() {
    ArduinoOTA.setHostname(MQTT_CLIENT_ID);
    ArduinoOTA.setPassword("ai-guardian-ota");

    ArduinoOTA.onStart([]() {
        String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
        Serial.println("OTA Start updating " + type);
    });
    ArduinoOTA.onEnd([]() {
        Serial.println("\nOTA Complete - restarting...");
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("End Failed");
    });
    ArduinoOTA.begin();
}

// ===================== SENSOR READING =====================
void readAllSensors() {
    readDHT();
    readPMS5003();
    readGas();
    readDigitalSensors();
    readCurrent();
    readVoltage();
    currentData.timestamp = millis();
    sensorValuesUpdated = true;
}

void readDHT() {
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
        currentData.temperature = t;
        currentData.humidity = h;
    }
}

void readPMS5003() {
    uint8_t buffer[32];
    int idx = 0;

    while (pmsSerial.available()) {
        int c = pmsSerial.read();
        if (c == 0x42 && idx == 0) {
            buffer[idx++] = c;
        } else if (idx > 0 || c == 0x42) {
            buffer[idx++] = c;
            if (idx >= 32) break;
        }
    }

    if (idx >= 32 && buffer[0] == 0x42 && buffer[1] == 0x4D) {
        uint16_t pm25 = (buffer[12] << 8) | buffer[13];
        uint16_t pm10 = (buffer[14] << 8) | buffer[15];
        currentData.dustPm25 = pm25 / 10.0f;
        currentData.dustPm10 = pm10 / 10.0f;
    }
}

void readGas() {
    int raw = analogRead(GAS_PIN);
    currentData.gasLevel = (raw / 4095.0f) * 100.0f;
}

void readDigitalSensors() {
    currentData.motionDetected = digitalRead(PIR_PIN) == HIGH;
    currentData.doorOpen = digitalRead(DOOR_PIN) == LOW;
    currentData.leakDetected = digitalRead(LEAK_PIN) == LOW;
}

void readCurrent() {
    int raw = analogRead(CURRENT_PIN);
    float voltage = (raw / 4095.0f) * 3.3f;
    float currentAmp = (voltage - 1.65f) / 0.066f;
    currentData.currentLeak = abs(currentAmp);
}

void readVoltage() {
    int rawIn = analogRead(VOLTAGE_PIN_1);
    int rawUps = analogRead(VOLTAGE_PIN_2);
    currentData.voltageInput = (rawIn / 4095.0f) * 250.0f;
    currentData.voltageUps = (rawUps / 4095.0f) * 20.0f;
}

// ===================== MAIN LOOP =====================
void loop() {
    unsigned long now = millis();

    ArduinoOTA.handle();
    wsSensorData.cleanupClients();

    if (!mqttClient.connected()) {
        if (now - lastMqttReconnect > 5000) {
            reconnectMQTT();
            lastMqttReconnect = now;
        }
    } else {
        mqttClient.loop();
    }

    if (now - lastReadingsTime >= READINGS_INTERVAL) {
        readAllSensors();
        lastReadingsTime = now;

        if (mqttClient.connected()) {
            publishSensorDataMQTT();
        }
    }

    if (now - lastWebsocketBroadcast >= WEBSOCKET_INTERVAL) {
        broadcastSensorData();
        lastWebsocketBroadcast = now;
    }

    updateOLED(currentData);

    if (now > 3600000 && now % 60000 < READINGS_INTERVAL) {
        if (WiFi.status() == WL_CONNECTED) {
            blinkLed(1);
        }
    }
}

void publishSensorDataMQTT() {
    StaticJsonDocument<512> doc;
    doc["node"] = MQTT_CLIENT_ID;
    doc["temperature"] = currentData.temperature;
    doc["humidity"] = currentData.humidity;
    doc["dust_pm25"] = currentData.dustPm25;
    doc["dust_pm10"] = currentData.dustPm10;
    doc["gas"] = currentData.gasLevel;
    doc["motion"] = currentData.motionDetected;
    doc["door"] = currentData.doorOpen;
    doc["leak"] = currentData.leakDetected;
    doc["current_leak"] = currentData.currentLeak;
    doc["voltage_input"] = currentData.voltageInput;
    doc["voltage_ups"] = currentData.voltageUps;
    doc["rssi"] = WiFi.RSSI();
    doc["uptime"] = millis() / 1000;
    doc["timestamp"] = now();

    char buffer[512];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_SENSORS, buffer);
    Serial.println("Published sensor data via MQTT");
}

// ===================== HELPERS =====================
void blinkLed(int times) {
    for (int i = 0; i < times; i++) {
        digitalWrite(LED_STATUS_PIN, HIGH);
        delay(100);
        digitalWrite(LED_STATUS_PIN, LOW);
        delay(100);
    }
}

const char* now() {
    static char buf[32];
    snprintf(buf, sizeof(buf), "%lu", millis());
    return buf;
}
