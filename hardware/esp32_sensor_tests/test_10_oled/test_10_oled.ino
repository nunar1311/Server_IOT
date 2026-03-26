// ============================================================
// TEST 10: MAN HINH OLED 1.3 INCH I2C (SH1106)
// ============================================================
// Cam bien: SH1106 1.3" OLED
// Giao tiep: I2C (SDA=IO21, SCL=IO22)
// Dia chi I2C: 0x3C
// Thu vien: Adafruit GFX + Adafruit SH110X
// ============================================================

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>
#include "config.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SH1106G display = Adafruit_SH1106G(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

unsigned long lastDisplayUpdate = 0;
unsigned long lastCounterUpdate = 0;
unsigned long oledUpdateInterval = OLED_UPDATE_INTERVAL;
int demoCounter = 0;

void oledSetup() {
    Serial.println("=== TEST 10: OLED 1.3 inch SH1106 I2C ===");
    Serial.print("SDA pin: "); Serial.println(OLED_SDA_PIN);
    Serial.print("SCL pin: "); Serial.println(OLED_SCL_PIN);
    Serial.print("I2C address: 0x"); Serial.println(OLED_I2C_ADDR, HEX);
    Serial.println("Khoi tao I2C...");

    Wire.begin(OLED_SDA_PIN, OLED_SCL_PIN);

    Serial.println("Khoi tao OLED...");
    if (!display.begin(OLED_I2C_ADDR, true)) {
        Serial.println("[LOI] Khong ket noi duoc OLED!");
        Serial.println("Kiem tra: VCC(3.3V), GND, SDA->IO21, SCL->IO22, Dia chi=0x3C");
        while (1) {
            delay(1000);
        }
    }

    Serial.println("[OK] OLED khoi dong!");
    display.display();
    delay(1500);
    display.clearDisplay();
    display.setTextSize(OLED_TEXT_SIZE);
    display.setTextColor(SH110X_WHITE);

    display.setCursor(0, 0);
    display.println("AI-GUARDIAN");
    display.println("OLED 1.3 SH1106");
    display.println("I2C Test");
    display.display();
    delay(2000);

    Serial.println("[OK] OLED san sang!");
    Serial.println();
}

void oledLoop() {
    unsigned long now = millis();

    if (now - lastCounterUpdate >= 100) {
        lastCounterUpdate = now;
        demoCounter++;
    }

    if (now - lastDisplayUpdate >= oledUpdateInterval) {
        lastDisplayUpdate = now;

        display.clearDisplay();

        display.setTextSize(2);
        display.setCursor(0, 0);
        display.println("=== OLED ===");

        display.setTextSize(1);

        display.setCursor(0, 20);
        display.println("1.3 inch SH1106 I2C");

        display.setCursor(0, 32);
        display.print("Counter: ");
        display.println(demoCounter);

        display.setCursor(0, 44);
        unsigned long uptimeSec = now / 1000;
        display.print("Uptime: ");
        display.print(uptimeSec);
        display.println("s");

        display.setCursor(0, 56);
        unsigned long sec = (now / 1000) % 60;
        unsigned long min = (now / 60000) % 60;
        unsigned long hr = (now / 3600000) % 24;
        char timeBuf[16];
        sprintf(timeBuf, "%02lu:%02lu:%02lu", hr, min, sec);
        display.print("Time: ");
        display.println(timeBuf);

        display.display();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    Serial.println();
    Serial.println("===========================================");
    Serial.println("  TEST 10: MAN HINH OLED 1.3 INCH SH1106");
    Serial.println("===========================================");
    Serial.println();
    oledSetup();
}

void loop() {
    oledLoop();
}
