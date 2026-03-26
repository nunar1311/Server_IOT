// ============================================================
// TEST 08 & 09: VOLTAGE DIVIDER - DIEN AP AC & UPS
// ============================================================
// Test 08: Dien ap AC (220V) qua Voltage Divider
// Chan GPIO: IO36 (INPUT ONLY - ADC1)
// Dac diem: R1=100k, R2=10k => chia 11 lan
//
// Test 09: Dien ap UPS (12V) qua Voltage Divider
// Chan GPIO: IO39 (INPUT ONLY - ADC1)
// Dac diem: R1=100k, R2=10k => chia 11 lan
//
// CANH BAO NGUY HIEM: Lam viec voi dien ap cao!
// Su dung bien tro hoac dieu chinh he so chia de hieu chinh
// ============================================================

#include <Arduino.h>
#include "config.h"

const int AC_VOLTAGE_ADC_PIN = AC_VOLTAGE_PIN;
const int UPS_VOLTAGE_ADC_PIN = UPS_VOLTAGE_PIN;

const float AC_DIVIDER_RATIO = (AC_R1 + AC_R2) / AC_R2;
const float UPS_DIVIDER_RATIO = (UPS_R1 + UPS_R2) / UPS_R2;

float acCalibration = AC_CALIBRATION;
float upsCalibration = UPS_CALIBRATION;

unsigned long lastReadTime = 0;
int acSampleCount = 0;
int upsSampleCount = 0;

void voltageSetup() {
    Serial.println("=== TEST 08 & 09: Voltage Divider (Dien Ap) ===");
    Serial.println();
    Serial.println("========== DIEN AP AC ==========");
    Serial.print("ADC Pin:    IO"); Serial.println(AC_VOLTAGE_ADC_PIN);
    Serial.print("R1:         "); Serial.print(AC_R1 / 1000.0, 0); Serial.println(" kOhm");
    Serial.print("R2:         "); Serial.print(AC_R2 / 1000.0, 0); Serial.println(" kOhm");
    Serial.print("Divider:    1:"); Serial.println(AC_DIVIDER_RATIO, 2);
    Serial.print("Calibration:"); Serial.println(AC_CALIBRATION, 3);
    Serial.println();
    Serial.println("========== DIEN AP UPS ==========");
    Serial.print("ADC Pin:    IO"); Serial.println(UPS_VOLTAGE_ADC_PIN);
    Serial.print("R1:         "); Serial.print(UPS_R1 / 1000.0, 0); Serial.println(" kOhm");
    Serial.print("R2:         "); Serial.print(UPS_R2 / 1000.0, 0); Serial.println(" kOhm");
    Serial.print("Divider:    1:"); Serial.println(UPS_DIVIDER_RATIO, 2);
    Serial.print("Calibration:"); Serial.println(UPS_CALIBRATION, 3);
    Serial.println();

    pinMode(AC_VOLTAGE_ADC_PIN, INPUT);
    pinMode(UPS_VOLTAGE_ADC_PIN, INPUT);

    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);

    Serial.println(">>> CANH BAO: Dien ap cao - can than khi su dung! <<<");
    Serial.println(">>> Su dung mach cach ly / bien tro de do an toan hon <<<");
    Serial.println();

    delay(1000);

    Serial.println("[OK] Voltage Divider khoi tao xong!");
    Serial.println();
}

float readACVoltage() {
    int raw = analogRead(AC_VOLTAGE_ADC_PIN);
    float vADC = raw * (3.3 / 4095.0);
    float vInput = vADC * AC_DIVIDER_RATIO;
    float vRMS = vInput / sqrt(2.0);
    return vRMS * acCalibration;
}

float readUPSVoltage() {
    int raw = analogRead(UPS_VOLTAGE_ADC_PIN);
    float vADC = raw * (3.3 / 4095.0);
    float vInput = vADC * UPS_DIVIDER_RATIO;
    return vInput * upsCalibration;
}

void voltageLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= 1000) {
        lastReadTime = now;

        float acVoltage = readACVoltage();
        float upsVoltage = readUPSVoltage();

        acSampleCount++;
        upsSampleCount++;

        Serial.println("========================================");
        Serial.println("--- Voltage Measurements ---");
        Serial.println();

        // AC Voltage
        Serial.print("[AC] Dien ap AC: ");
        Serial.print(acVoltage, 1); Serial.print(" V");
        if (acVoltage > AC_VOLTAGE_MAX) {
            Serial.println(" [VUOT CAO!]");
        } else if (acVoltage < AC_VOLTAGE_MIN) {
            Serial.println(" [THAP!]");
        } else {
            Serial.println(" [BT]");
        }
        Serial.print("       Raw ADC:  "); Serial.println(analogRead(AC_VOLTAGE_ADC_PIN));
        Serial.print("       Samples: "); Serial.println(acSampleCount);

        // UPS Voltage
        Serial.println();
        Serial.print("[UPS] Dien ap UPS: ");
        Serial.print(upsVoltage, 2); Serial.print(" V");
        if (upsVoltage > UPS_VOLTAGE_MAX) {
            Serial.println(" [VUOT CAO!]");
        } else if (upsVoltage < UPS_VOLTAGE_MIN) {
            Serial.println(" [SAP HET!]");
        } else {
            Serial.println(" [BT]");
        }
        Serial.print("        Raw ADC:  "); Serial.println(analogRead(UPS_VOLTAGE_ADC_PIN));
        Serial.print("        Samples: "); Serial.println(upsSampleCount);

        Serial.println();
        Serial.println("========================================");

        // Alerts
        if (acVoltage > AC_VOLTAGE_MAX || acVoltage < AC_VOLTAGE_MIN) {
            Serial.println("[CANH BAO AC] Dien ap AC khong on dinh!");
        }
        if (upsVoltage < UPS_VOLTAGE_MIN) {
            Serial.println("[CANH BAO UPS] UPS sap het - can sac!");
        }
        if (upsVoltage > UPS_VOLTAGE_MAX) {
            Serial.println("[CANH BAO UPS] UPS qua ap - nguy hiem!");
        }

        Serial.println();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    voltageSetup();
}

void loop() {
    voltageLoop();
}
