// ============================================================
// TEST 05: CAM BIEN ACS712 - RO DIEN (DONG DIEN)
// ============================================================
// Cam bien: ACS712 (30A model)
// Chan GPIO: IO35 (INPUT ONLY - ADC1)
// Dien ap: 5V
// Dac diem: Cam bien dong dien AC dua tren hieu ung Hall
// Do chinh xac: 66mV/A (model 30A)
// ============================================================

#include <Arduino.h>
#include "config.h"

const int NUM_SAMPLES = 1000;
unsigned long lastReadTime = 0;
int sampleCount = 0;

float readACS712Voltage() {
    int raw = analogRead(ACS712_PIN);
    return raw * (3.3 / 4095.0);
}

float readACS712ACCurrent() {
    float voltage;
    float peakVoltage = 0;
    unsigned long startMicros = micros();
    int count = 0;

    while (micros() - startMicros < 1000000) {
        voltage = analogRead(ACS712_PIN) * (3.3 / 4095.0);
        if (voltage > peakVoltage) {
            peakVoltage = voltage;
        }
        count++;
        delayMicroseconds(200);
    }

    float Vpp = peakVoltage * 2;
    float Vrms = Vpp / (2.0 * sqrt(2.0));
    float zeroVoltage = 1.65;
    float current = (Vrms - zeroVoltage) / ACS712_SENSITIVITY;
    return abs(current);
}

void acs712Setup() {
    Serial.println("=== TEST 05: ACS712 30A (Ro Dien) ===");
    Serial.print("ADC Pin: IO"); Serial.println(ACS712_PIN);
    Serial.print("Sensitivity: "); Serial.print(ACS712_SENSITIVITY, 3); Serial.println(" V/A");
    Serial.println();

    pinMode(ACS712_PIN, INPUT);

    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);

    Serial.println("Dang do dien ap offset (khong tai)...");
    delay(2000);

    float offsetSum = 0;
    const int offsetSamples = 500;
    for (int i = 0; i < offsetSamples; i++) {
        offsetSum += readACS712Voltage();
        delay(10);
    }
    float offsetVoltage = offsetSum / offsetSamples;

    Serial.print("[OK] Offset voltage (khong tai): "); Serial.print(offsetVoltage, 4); Serial.println(" V");
    Serial.print("[INFO] Dong dien offset: "); Serial.print((offsetVoltage - 1.65) / ACS712_SENSITIVITY * 1000, 2); Serial.println(" mA");
    Serial.println();
    Serial.println("NOI CAC DAY TAI VAO DONG DIEN AC CAN DO!");
    Serial.println();
}

void acs712Loop() {
    unsigned long now = millis();
    if (now - lastReadTime >= 1000) {
        lastReadTime = now;
        sampleCount++;

        float rawVoltage = readACS712Voltage();
        float current = readACS712ACCurrent();

        Serial.print("--- ACS712 [Sample #"); Serial.print(sampleCount); Serial.println("] ---");
        Serial.print("ADC Voltage:  "); Serial.print(rawVoltage, 4); Serial.println(" V");
        Serial.print("Dong dien AC: "); Serial.print(current, 4); Serial.println(" A");

        if (rawVoltage < 1.5) {
            Serial.println("[INFO] Diem 0: Dung duoi 1.65V");
        } else if (rawVoltage > 1.8) {
            Serial.println("[INFO] Diem 0: Dung tren 1.65V");
        } else {
            Serial.println("[INFO] Diem 0: Gan 1.65V (tot)");
        }

        float power = current * 220.0;
        Serial.print("Cong suat uoc tinh: "); Serial.print(power, 1); Serial.println(" W");

        if (current > LEAK_CURRENT_THRESHOLD) {
            Serial.println("[CANH BAO] Phat hien dong dien ro! Co the co su co!");
        } else {
            Serial.println("[OK] Khong co ro dien");
        }

        Serial.println();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    acs712Setup();
}

void loop() {
    acs712Loop();
}
