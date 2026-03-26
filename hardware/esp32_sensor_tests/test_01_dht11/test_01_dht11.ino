// ============================================================
// TEST 01: CAM BIEN DHT11 - NHIET DO / DO AM
// ============================================================
// Cam bien: DHT11
// Chan GPIO: IO32
// Dien ap: 3.3V / 5V
// Thu vien: DHT sensor library (Adafruit)
// ============================================================

#include <Arduino.h>
#include <DHT.h>
#include "config.h"

DHT dht(DHT_PIN, DHT_TYPE);

unsigned long lastReadTime = 0;

void dhtSetup() {
    Serial.println("=== TEST 01: DHT11 (Nhiet do / Do am) ===");
    Serial.print("Chan GPIO: "); Serial.println(DHT_PIN);
    Serial.println("Khoi tao cam bien...");

    dht.begin();

    Serial.println("Cho 2s de cam bien on dinh...");
    delay(2000);

    float testTemp = dht.readTemperature();
    float testHum = dht.readHumidity();

    if (isnan(testTemp) || isnan(testHum)) {
        Serial.println("[LOI] Khong doc duoc du lieu tu DHT11!");
        Serial.println("Kiem tra: VCC(3.3V/5V), GND, Data->IO32");
    } else {
        Serial.println("[OK] DHT11 hoat dong!");
        Serial.print("Nhiet do test: "); Serial.print(testTemp); Serial.println(" *C");
        Serial.print("Do am test: "); Serial.print(testHum); Serial.println(" %");
    }
    Serial.println();
}

void dhtLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= DHT_READ_INTERVAL) {
        lastReadTime = now;

        float humidity = dht.readHumidity();
        float temperature = dht.readTemperature();
        float fahrenheit = dht.readTemperature(true);

        if (isnan(humidity) || isnan(temperature)) {
            Serial.println("[LOI] Khong doc duoc du lieu!");
            return;
        }

        float heatIndex = dht.computeHeatIndex(fahrenheit, humidity);

        Serial.println("--- DHT11 Data ---");
        Serial.print("Nhiet do:   "); Serial.print(temperature, 1);
        Serial.print(" *C | "); Serial.print(fahrenheit, 1); Serial.println(" *F");
        Serial.print("Do am:      "); Serial.print(humidity, 1); Serial.println(" %");
        Serial.print("Heat Index: "); Serial.print(heatIndex, 1); Serial.println(" *F");

        // Canh bao nhiet do
        if (temperature > TEMP_MAX) {
            Serial.println("[CANH BAO] Nhiet do qua cao!");
        } else if (temperature < TEMP_MIN) {
            Serial.println("[CANH BAO] Nhiet do qua thap!");
        }

        // Canh bao do am
        if (humidity > HUMIDITY_MAX) {
            Serial.println("[CANH BAO] Do am qua cao!");
        } else if (humidity < HUMIDITY_MIN) {
            Serial.println("[CANH BAO] Do am qua thap!");
        }
        Serial.println();
    }
}

void setup() {
    Serial.begin(115200);
    delay(500);
    dhtSetup();
}

void loop() {
    dhtLoop();
}
