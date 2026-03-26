// ============================================================
// TEST 04: CAM BIEN RO NUOC (LEAK SENSOR)
// ============================================================
// Cam bien: Leak Sensor (Cam bien ro nuoc)
// Chan GPIO: IO34 (INPUT ONLY - ADC1)
// Dien ap: 3.3V
// Dac diem: Phat hien nuoc cham vao 2 day cam bien
// ============================================================

#include <Arduino.h>
#include "config.h"

const int LEAK_SENSOR_PIN = LEAK_PIN;
const int LED_INDICATOR_PIN = LEAK_LED_PIN;

bool leakDetected = false;
bool lastLeakState = false;
unsigned long leakStartTime = 0;
unsigned long lastReadTime = 0;
int dryCount = 0;
int wetCount = 0;

void leakSetup() {
    Serial.println("=== TEST 04: Leak Sensor (Ro Nuoc) ===");
    Serial.print("Sensor Pin: IO"); Serial.println(LEAK_SENSOR_PIN);
    Serial.print("LED Pin: IO"); Serial.println(LED_INDICATOR_PIN);
    Serial.println();

    pinMode(LEAK_SENSOR_PIN, INPUT);
    pinMode(LED_INDICATOR_PIN, OUTPUT);

    digitalWrite(LED_INDICATOR_PIN, LOW);

    Serial.println("Dang cho cam bien bat dau doc...");
    delay(500);

    int initialReading = digitalRead(LEAK_SENSOR_PIN);
    Serial.print("Trang thai ban dau: ");
    Serial.println(initialReading == LOW ? "KHO (Khong co nuoc)" : "AM (Co nuoc!)");

    Serial.println();
    Serial.println("Tha 1 giot nuoc vao cam bien de test...");
    Serial.println("Hoac lam uot 2 day cam bien de test.");
    Serial.println();
}

void leakLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= 500) {
        lastReadTime = now;

        int sensorValue = digitalRead(LEAK_SENSOR_PIN);
        leakDetected = (sensorValue == LOW);

        digitalWrite(LED_INDICATOR_PIN, leakDetected ? HIGH : LOW);

        Serial.print("--- Leak Sensor ["); Serial.print(millis() / 1000); Serial.println("s] ---");
        Serial.print("Sensor:  ");
        if (leakDetected) {
            Serial.println("PHAI HUNG RO NUOC!");
            wetCount++;
        } else {
            Serial.println("Khong co ro nuoc");
            dryCount++;
        }
        Serial.print("LED:     "); Serial.println(leakDetected ? "BAT (Do)" : "TAT (Xanh)");

        if (leakDetected && !lastLeakState) {
            leakStartTime = now;
            Serial.println("[CANH BAO] Phat hien ro nuoc!");
            Serial.print("[STAMP] Thoi gian bat dau: "); Serial.print(leakStartTime / 1000); Serial.println("s");
        } else if (leakDetected && lastLeakState) {
            unsigned long duration = (now - leakStartTime) / 1000;
            Serial.print("[STAMP] Thoi gian ro: "); Serial.print(duration); Serial.println("s");
        }

        if (!leakDetected && lastLeakState) {
            unsigned long totalLeak = (now - leakStartTime) / 1000;
            Serial.print("[RECAP] Tong thoi gian ro: "); Serial.print(totalLeak); Serial.println("s");
            Serial.println("[INFO] Da khoi phuc - khong con ro nuoc");
        }

        Serial.print("Thong ke: Lan phat hien="); Serial.print(wetCount);
        Serial.print(" | Lan kho="); Serial.print(dryCount);
        Serial.print(" | Hien tai="); Serial.println(leakDetected ? "RO" : "KHO");
        Serial.println();
        lastLeakState = leakDetected;
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    leakSetup();
}

void loop() {
    leakLoop();
}
