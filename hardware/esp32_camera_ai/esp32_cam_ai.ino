# ============================================================
# AI-Guardian - ESP32-CAM AI Detection Node
# Phat hien lua, khuon mat, phat hien nghi, phat hien nghe
# ============================================================
//
// IMPORTANT: This is an Arduino sketch (.ino) file.
// For ESP32-CAM with ESP32-WROVER or ESP32-S module.
// Use AI Thinker ESP32-CAM board settings in Arduino IDE.
// ============================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <esp_camera.h>
#include <base64.h>

// ===================== CONFIGURATION =====================
#define WIFI_SSID       "YOUR_WIFI_SSID"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD"
#define MQTT_SERVER     "192.168.1.100"
#define MQTT_PORT       1883
#define MQTT_CLIENT_ID  "esp32_cam_ai"

#define MQTT_TOPIC_CAM       "ai-guardian/camera"
#define MQTT_TOPIC_CAM_ALERT "ai-guardian/camera/alert"
#define MQTT_TOPIC_CAM_STATUS "ai-guardian/camera/status"

// ===================== CAMERA PINS (AI Thinker ESP32-CAM) =====================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// LED Flash
#define FLASH_GPIO_NUM    4

// ===================== STATE =====================
bool mqttConnected = false;
unsigned long lastFrameTime = 0;
unsigned long lastAlertTime = 0;
const unsigned long FRAME_INTERVAL = 5000;  // 5 seconds between frames

// Simulated AI detection (replace with actual TFLite model inference)
bool fireDetected = false;
bool personDetected = false;
bool fallDetected = false;

// ===================== OBJECTS =====================
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ===================== SETUP =====================
void setup() {
    Serial.begin(115200);

    initCamera();
    initWiFi();
    initMQTT();

    pinMode(FLASH_GPIO_NUM, OUTPUT);
    digitalWrite(FLASH_GPIO_NUM, LOW);

    Serial.println("ESP32-CAM AI Node started");
}

// ===================== CAMERA INIT =====================
void initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.frame_size = FRAME_SIZE_SVGA;   // 800x600
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 2;

    if (config.pixel_format == PIXFORMAT_JPEG) {
        if (psramFound()) {
            config.fb_count = 2;
            config.jpeg_quality = 10;
        } else {
            config.fb_count = 1;
            config.jpeg_quality = 12;
        }
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x\n", err);
        return;
    }

    sensor_t* s = esp_camera_sensor_get();
    if (s != NULL) {
        s->set_brightness(s, 0);
        s->set_contrast(s, 0);
        s->set_saturation(s, 0);
        s->set_whitebal(s, 1);
        s->set_awb_gain(s, 1);
        s->set_wb_mode(s, 0);
        s->set_exposure_ctrl(s, 1);
        s->set_aec2(s, 0);
        s->set_ae_level(s, 0);
        s->set_aec_value(s, 300);
        s->set_gain_ctrl(s, 1);
        s->set_agc_gain(s, 0);
        s->set_gainceiling(s, (gainceiling_t)0);
        s->set_bpc(s, 0);
        s->set_wpc(s, 1);
        s->set_raw_gma(s, 1);
        s->set_lenc(s, 1);
        s->set_hmirror(s, 0);
        s->set_vflip(s, 0);
        s->set_dcw(s, 1);
        s->set_colorbar(s, 0);
    }
}

// ===================== WIFI & MQTT =====================
void initWiFi() {
    Serial.print("Connecting to WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 30) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" Connected! IP: " + WiFi.localIP().toString());
    }
}

void initMQTT() {
    mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.println("MQTT message received");
}

bool reconnectMQTT() {
    if (mqttClient.connected()) return true;
    Serial.print("MQTT connecting...");
    if (mqttClient.connect(MQTT_CLIENT_ID)) {
        Serial.println("connected");
        return true;
    }
    Serial.print(" failed, rc=");
    Serial.println(mqttClient.state());
    return false;
}

// ===================== AI DETECTION (Simulated) =====================
// In production, integrate TensorFlow Lite Micro:
// #include <TensorFlowLite_ESP32.h>
// #include <model.h>  // your .tflite model converted to byte array

bool runAIDetection(camera_fb_t* fb) {
    // =========================================================
    // PLACEHOLDER: Replace with actual TFLite inference.
    //
    // Example integration:
    //   tflite::MicroInterpreter interpreter(model, resolver, ...
    //   interpreter.Invoke();
    //   float* output = interpreter.output(0);
    //   fireDetected = output[0] > 0.75f;
    //   personDetected = output[1] > 0.80f;
    //   fallDetected = output[2] > 0.85f;
    // =========================================================

    // Simulate detection based on brightness/colors for demo
    // In production, use actual model inference
    static unsigned long lastSimTime = 0;
    if (millis() - lastSimTime > 10000) {
        // Simulate random detection for testing
        fireDetected   = false;
        personDetected = false;
        fallDetected   = false;
        lastSimTime = millis();
    }

    return fireDetected || personDetected || fallDetected;
}

// ===================== MAIN LOOP =====================
void loop() {
    unsigned long now = millis();

    if (!mqttClient.connected()) {
        reconnectMQTT();
    } else {
        mqttClient.loop();
    }

    if (now - lastFrameTime >= FRAME_INTERVAL) {
        captureAndProcess();
        lastFrameTime = now;
    }

    delay(10);
}

void captureAndProcess() {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Camera capture failed");
        return;
    }

    Serial.printf("Captured %d bytes (%dx%d)\n", fb->len, fb->width, fb->height);

    bool detected = runAIDetection(fb);

    if (detected && (now() - lastAlertTime > 60000)) {
        String alertType;
        if (fireDetected) alertType = "fire";
        else if (personDetected) alertType = "person";
        else if (fallDetected) alertType = "fall";

        publishAlert(alertType, fb);
        lastAlertTime = now();
    }

    // Periodically publish frame metadata (not full image)
    if (mqttClient.connected()) {
        char meta[256];
        snprintf(meta, sizeof(meta),
            "{\"node\":\"esp32_cam\",\"detections\":{"
            "\"fire\":%s,\"person\":%s,\"fall\":%s},"
            "\"frame_size\":%d,\"rssi\":%d,\"uptime\":%lu}",
            fireDetected ? "true" : "false",
            personDetected ? "true" : "false",
            fallDetected ? "true" : "false",
            fb->len,
            WiFi.RSSI(),
            millis() / 1000
        );
        mqttClient.publish(MQTT_TOPIC_CAM, meta);
    }

    esp_camera_fb_return(fb);
}

void publishAlert(String type, camera_fb_t* fb) {
    StaticJsonDocument<512> doc;
    doc["node"] = MQTT_CLIENT_ID;
    doc["alert_type"] = type;
    doc["confidence"] = 0.92f;  // placeholder
    doc["timestamp"] = now();
    doc["rssi"] = WiFi.RSSI();

    char buffer[512];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_CAM_ALERT, buffer);

    Serial.println("ALERT: " + type + " detected!");

    // Flash LED
    for (int i = 0; i < 3; i++) {
        digitalWrite(FLASH_GPIO_NUM, HIGH);
        delay(200);
        digitalWrite(FLASH_GPIO_NUM, LOW);
        delay(200);
    }
}

unsigned long now() {
    return millis();
}
