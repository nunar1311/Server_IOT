#ifndef SENSORS_H
#define SENSORS_H

// ============================================================
// AI-Guardian - Sensor Reading Functions
// ============================================================

#include <DHT.h>
#include <HardwareSerial.h>

struct SensorReading {
    float temperature;
    float humidity;
    float dustPm25;
    float dustPm10;
    float gasLevel;
    bool  motion;
    bool  door;
    bool  leak;
    float currentLeak;
    float voltageInput;
    float voltageUps;
};

void initSensors() {
    dht.begin();
    pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);

    pinMode(PIR_PIN, INPUT);
    pinMode(DOOR_PIN, INPUT_PULLUP);
    pinMode(LEAK_PIN, INPUT_PULLUP);
}

SensorReading readSensors() {
    SensorReading data;
    data.temperature = readDHT_Temperature();
    data.humidity    = readDHT_Humidity();
    readPMS5003(&data.dustPm25, &data.dustPm10);
    data.gasLevel      = readGasLevel();
    data.motion        = digitalRead(PIR_PIN) == HIGH;
    data.door          = digitalRead(DOOR_PIN) == LOW;
    data.leak          = digitalRead(LEAK_PIN) == LOW;
    data.currentLeak   = readCurrentLeak();
    data.voltageInput  = readVoltageInput();
    data.voltageUps    = readVoltageUps();
    return data;
}

float readDHT_Temperature() {
    float t = dht.readTemperature();
    return isnan(t) ? 0.0f : t;
}

float readDHT_Humidity() {
    float h = dht.readHumidity();
    return isnan(h) ? 0.0f : h;
}

void readPMS5003(float* pm25, float* pm10) {
    uint8_t buf[32];
    int idx = 0;
    while (pmsSerial.available()) {
        int c = pmsSerial.read();
        if (c == 0x42 && idx == 0) buf[idx++] = c;
        else if (idx > 0) {
            buf[idx++] = c;
            if (idx >= 32) break;
        }
    }
    if (idx >= 32 && buf[0] == 0x42 && buf[1] == 0x4D) {
        *pm25 = ((buf[12] << 8) | buf[13]) / 10.0f;
        *pm10 = ((buf[14] << 8) | buf[15]) / 10.0f;
    }
}

float readGasLevel() {
    int raw = analogRead(GAS_PIN);
    return (raw / 4095.0f) * 100.0f;
}

float readCurrentLeak() {
    int raw = analogRead(CURRENT_PIN);
    float voltage = (raw / 4095.0f) * 3.3f;
    float currentAmp = (voltage - 1.65f) / 0.066f;
    return abs(currentAmp);
}

float readVoltageInput() {
    int raw = analogRead(VOLTAGE_PIN_1);
    return (raw / 4095.0f) * 250.0f;
}

float readVoltageUps() {
    int raw = analogRead(VOLTAGE_PIN_2);
    return (raw / 4095.0f) * 20.0f;
}

bool checkThresholds(const SensorReading& data) {
    return data.temperature > TEMP_CRITICAL ||
           data.gasLevel > GAS_WARNING ||
           data.dustPm25 > DUST_WARNING ||
           data.currentLeak > CURRENT_LEAK_WARNING;
}

#endif // SENSORS_H
