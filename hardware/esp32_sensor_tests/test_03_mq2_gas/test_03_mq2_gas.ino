// ============================================================
// TEST 03: CAM BIEN MQ-2 - KHOI / GAS
// ============================================================
// Cam bien: MQ-2 (Khoi, Gas, LNG, LPG, Alcohol, Propane, Hydrogen)
// Chan GPIO: IO33 (Analog)
// Dien ap: 5V
// Dac diem: Can doi 24-48h, preheat truoc khi su dung
// ============================================================

#include <Arduino.h>
#include "config.h"

const int MQ2_ADC_PIN = MQ2_ANA_PIN;
const int MQ2_DIGITAL_PIN = MQ2_D0_PIN;

unsigned long lastReadTime = 0;

float Ro = 10.0;
unsigned long lastCalibrationTime = 0;
bool calibrated = false;

// LPG, CO, Smoke
float LPGCurve[3]  = { 2.3, 0.21, -0.47 };
float COCurve[3]   = { 1.0, 0.27, -0.55 };
float SmokeCurve[3]= { 2.8, 0.53, -0.43 };

void mq2Setup() {
    Serial.println("=== TEST 03: MQ-2 (Khoi / Gas) ===");
    Serial.print("ADC Pin: IO"); Serial.println(MQ2_ADC_PIN);
    Serial.print("Digital Pin: IO"); Serial.println(MQ2_DIGITAL_PIN);
    Serial.println();

    pinMode(MQ2_ADC_PIN, INPUT);
    pinMode(MQ2_DIGITAL_PIN, INPUT);

    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);

    Serial.println(">>> LUU Y: MQ-2 can 24-48h de doi, 5-10 phut de khoi dong!");
    Serial.println(">>> Neu la lan dau su dung, bo tien trinh nay trong setup()...");
    Serial.println();

    Serial.println("Dang calibrating... (vui long cho 5 phut o khong khi sach)...");
    Ro = mq2Calibrate();
    calibrated = true;
    Serial.print("[OK] Calibrating xong! Ro = "); Serial.print(Ro); Serial.println(" kOhm");
    Serial.println();
}

float readMQ2Resistance() {
    int rawADC = analogRead(MQ2_ADC_PIN);
    float voltage = rawADC * (3.3 / 4095.0);
    float VRL = voltage;
    float RL = RL_VALUE;
    float RS = (3.3 * RL / VRL) - RL;
    return RS;
}

float readMQ2Raw() {
    return (float)analogRead(MQ2_ADC_PIN);
}

float readMQ2Voltage() {
    int raw = analogRead(MQ2_ADC_PIN);
    return raw * (3.3 / 4095.0);
}

float mq2Calibrate() {
    float val = 0.0;
    const int samples = 500;
    for (int i = 0; i < samples; i++) {
        val += readMQ2Resistance();
        delay(10);
    }
    val = val / samples;
    val = val / RO_CLEAN_AIR_FACTOR;
    return val;
}

int readMQ2MQ2(float rs_ro_ratio, const float* curve) {
    return (int)(pow(10, ((log(rs_ro_ratio) - curve[1]) / curve[2]) + curve[0]));
}

void mq2Loop() {
    unsigned long now = millis();
    if (now - lastReadTime >= MQ2_READ_INTERVAL) {
        lastReadTime = now;

        float rawValue = readMQ2Raw();
        float voltage = readMQ2Voltage();
        float rs = readMQ2Resistance();
        float rs_ro_ratio = rs / Ro;

        int lpg = readMQ2MQ2(rs_ro_ratio, LPGCurve);
        int co = readMQ2MQ2(rs_ro_ratio, COCurve);
        int smoke = readMQ2MQ2(rs_ro_ratio, SmokeCurve);

        Serial.println("--- MQ-2 Data ---");
        Serial.print("ADC Raw:    "); Serial.println((int)rawValue);
        Serial.print("Voltage:    "); Serial.print(voltage, 3); Serial.println(" V");
        Serial.print("RS:         "); Serial.print(rs, 2); Serial.println(" kOhm");
        Serial.print("RS/RO:      "); Serial.print(rs_ro_ratio, 3);
        if (!calibrated) {
            Serial.println(" (chua calibrate)");
        } else {
            Serial.println();
        }
        Serial.println("--- Nong do (ppm) ---");
        Serial.print("LPG:        "); Serial.print(lpg); Serial.println(" ppm");
        Serial.print("CO:         "); Serial.print(co); Serial.println(" ppm");
        Serial.print("Smoke:      "); Serial.print(smoke); Serial.println(" ppm");

        int digitalVal = digitalRead(MQ2_DIGITAL_PIN);
        Serial.print("Digital Out: "); Serial.println(digitalVal == HIGH ? "CO Gas!" : "Khong phat hien");

        if (rawValue > GAS_THRESHOLD) {
            Serial.println("[CANH BAO] Nong do gas/khoi vuot nguong!");
        }
        Serial.println();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    mq2Setup();
}

void loop() {
    mq2Loop();
}
