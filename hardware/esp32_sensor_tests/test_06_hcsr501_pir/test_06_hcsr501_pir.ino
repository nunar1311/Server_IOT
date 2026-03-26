// ============================================================
// TEST 06: CAM BIEN HC-SR501 - CHUYEN DONG (PIR)
// ============================================================
// Cam bien: HC-SR501 (Passive Infrared Sensor)
// Chan GPIO: IO26
// Dien ap: 5V
// Dac diem: Phat hien nguoi/chuyen dong nguoi trong pham vi 3-7m
// Time delay: 0.3s - 5min (dieu chinh bang bien tro)
// Sensitivity: 3-7m (dieu chinh bang bien tro)
// ============================================================

#include <Arduino.h>
#include "config.h"

const int LED_PIN = PIR_LED_PIN;

bool motionDetected = false;
bool lastMotionState = false;
unsigned long motionStartTime = 0;
unsigned long lastReadTime = 0;
unsigned long motionCount = 0;
unsigned long noMotionCount = 0;
unsigned long lastMotionTime = 0;

void pirSetup() {
    Serial.println("=== TEST 06: HC-SR501 (Chuyen Dong) ===");
    Serial.print("PIR Pin: IO"); Serial.println(PIR_PIN);
    Serial.print("LED Pin: IO"); Serial.println(LED_PIN);
    Serial.println();

    pinMode(PIR_PIN, INPUT);
    pinMode(LED_PIN, OUTPUT);

    digitalWrite(LED_PIN, LOW);

    Serial.println("Cho cam bien on dinh (30s)...");
    Serial.println("Khong di chuyen trong luc nay!");
    delay(1000);
    Serial.println("Dang on dinh...");
    delay(29000);

    int testReading = digitalRead(PIR_PIN);
    Serial.println("[OK] Cam bien on dinh!");
    Serial.print("Trang thai test: ");
    Serial.println(testReading == HIGH ? "PHAT HIEN CHUYEN DONG!" : "Khong co chuyen dong");
    Serial.println();
    Serial.println("Bay gio cam bien san sang! Di chuyen truoc no de test.");
    Serial.println();
}

void pirLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= 200) {
        lastReadTime = now;

        int pirValue = digitalRead(PIR_PIN);
        motionDetected = (pirValue == HIGH);

        digitalWrite(LED_PIN, motionDetected ? HIGH : LOW);

        unsigned long uptime = now / 1000;

        if (motionDetected) {
            if (!lastMotionState) {
                motionCount++;
                motionStartTime = now;
                lastMotionTime = now;
                Serial.print("--- HC-SR501 ["); Serial.print(uptime); Serial.println("s] ---");
                Serial.println("*** CHUYEN DONG PHAT HIEN! ***");
                Serial.print("Motion #"); Serial.print(motionCount);
                Serial.print(" | Thoi gian: "); Serial.print(motionStartTime / 1000); Serial.println("s");
            }
            lastMotionState = true;
        } else {
            if (lastMotionState) {
                unsigned long motionDuration = (now - motionStartTime) / 1000;
                Serial.print("--- HC-SR501 ["); Serial.print(uptime); Serial.println("s] ---");
                Serial.print("Chuyen dong ket thuc!");
                Serial.print(" | Thoi gian: "); Serial.print(motionDuration); Serial.println("s");
            }
            lastMotionState = false;
            noMotionCount++;
        }

        Serial.print("--- HC-SR501 ["); Serial.print(uptime); Serial.println("s] ---");
        Serial.print("Trang thai: ");
        if (motionDetected) {
            Serial.println("CO NGUOI!");
        } else {
            Serial.println("Khong co nguoi");
        }
        Serial.print("LED Indicator: "); Serial.println(motionDetected ? "BAT (Do)" : "TAT");
        Serial.print("Tong so lan phat hien: "); Serial.println(motionCount);

        if (lastMotionTime > 0 && !motionDetected) {
            unsigned long timeSinceLast = (now - lastMotionTime) / 1000;
            if (timeSinceLast < 10) {
                Serial.print("[STAMP] Thoi gian tu lan phat hien cuoi: "); Serial.print(timeSinceLast); Serial.println("s");
            }
        }

        Serial.println();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    pirSetup();
}

void loop() {
    pirLoop();
}
