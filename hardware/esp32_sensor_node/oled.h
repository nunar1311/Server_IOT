// ============================================================
// AI-Guardian - OLED Display Module (SH1106 1.3" I2C)
// ============================================================

#ifndef OLED_H
#define OLED_H

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "config.h"

#define SCREEN_WIDTH  128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1

Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

unsigned long lastOledUpdate = 0;
bool oledInitialized = false;

void initOLED() {
    Serial.print("Khoi tao I2C (SDA=");
    Serial.print(OLED_SDA_PIN);
    Serial.print(", SCL=");
    Serial.print(OLED_SCL_PIN);
    Serial.println(")...");
    Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);

    Serial.print("Khoi tao OLED SH1106 (addr=0x");
    Serial.print(OLED_I2C_ADDR, HEX);
    Serial.println(")...");
    if (!display.begin(OLED_I2C_ADDR, true)) {
        Serial.println("[LOI] Khong ket noi duoc OLED! Kiem tra day ket noi.");
        return;
    }

    display.display();
    delay(1000);
    display.clearDisplay();
    display.setTextSize(OLED_TEXT_SIZE);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 0);

    display.println(" AI-GUARDIAN ");
    display.println(" Khoi dong...");
    display.println("");
    display.println(" IP: " + WiFi.localIP().toString());
    display.display();
    delay(1500);

    oledInitialized = true;
    Serial.println("[OK] OLED san sang!");
}

void updateOLED(const SensorData& data) {
    if (!oledInitialized) return;

    unsigned long now = millis();
    if (now - lastOledUpdate < OLED_UPDATE_INTERVAL) return;
    lastOledUpdate = now;

    display.clearDisplay();

    // Dong 1: Tieu de
    display.setTextSize(1);
    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 0);
    display.println("== AI-GUARDIAN ==");

    // Dong 2: Nhiet do + Do am
    display.setCursor(0, 10);
    display.print("T:");
    display.print(data.temperature, 1);
    display.print("C H:");
    display.print(data.humidity, 1);
    display.print("%");

    // Dong 3: Bui PM2.5
    display.setCursor(64, 10);
    display.print("PM2.5:");
    display.print(data.dustPm25, 1);
    display.print("ug");

    // Dong 4: Gas
    display.setCursor(0, 20);
    display.print("Gas:");
    display.print(data.gasLevel, 0);
    display.print("%  Curr:");
    display.print(data.currentLeak, 1);
    display.print("A");

    // Dong 5: Dien ap
    display.setCursor(0, 30);
    display.print("AC:");
    display.print(data.voltageInput, 0);
    display.print("V UPS:");
    display.print(data.voltageUps, 1);
    display.print("V");

    // Dong 6: Trang thai
    display.setCursor(0, 40);
    if (data.motionDetected) {
        display.print("[CHUYEN DONG!]");
    } else if (data.leakDetected) {
        display.print("[RO NUOC!]");
    } else if (data.doorOpen) {
        display.print("[CUA MO!]");
    } else {
        display.print("OK-Normal");
    }

    // Dong 7: RSSI & Uptime
    display.setCursor(0, 50);
    display.print("RSSI:");
    display.print(WiFi.RSSI());
    display.print("dBm ");
    display.print("Uptime:");
    unsigned long uptimeSec = millis() / 1000;
    if (uptimeSec < 3600) {
        display.print(uptimeSec / 60);
        display.print("m");
    } else {
        display.print(uptimeSec / 3600);
        display.print("h");
    }

    display.display();
}

void showAlertOnOLED(const char* alertType, const char* message) {
    if (!oledInitialized) return;

    display.clearDisplay();
    display.setTextSize(1);

    display.setTextColor(SH110X_WHITE);
    display.setCursor(0, 0);
    display.println("== CANH BAO ==");

    display.setCursor(0, 12);
    display.println(alertType);

    display.setCursor(0, 24);
    display.println(message);

    unsigned long sec = (millis() / 1000) % 60;
    unsigned long min = (millis() / 60000) % 60;
    unsigned long hr = (millis() / 3600000) % 24;
    char timeBuf[16];
    sprintf(timeBuf, "%02lu:%02lu:%02lu", hr, min, sec);
    display.setCursor(0, 40);
    display.print("Time: ");
    display.println(timeBuf);

    display.display();
}

#endif // OLED_H
