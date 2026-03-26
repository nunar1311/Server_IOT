// ============================================================
// MASTER TEST - TEST TAT CA CAM BIEN
// ============================================================
// Test tat ca cam bien cung luc tren ESP32 NodeMCU-32S
// Su dung thu vien tu folder hien tai
// ============================================================

// Comment/Uncomment dong #define de chon test muon chay
#define TEST_DHT11
#define TEST_PMS5003
#define TEST_MQ2
#define TEST_LEAK
#define TEST_ACS712
#define TEST_PIR
#define TEST_REED
#define TEST_VOLTAGE

#include <Arduino.h>
#include "config.h"

#ifdef TEST_DHT11
#include <DHT.h>
DHT dht(DHT_PIN, DHT_TYPE);
unsigned long dhtLastRead = 0;
#endif

#ifdef TEST_PMS5003
#include <HardwareSerial.h>
HardwareSerial pmsSerial(2);
unsigned char pmsBuffer[32];
int pmsIndex = 0;
unsigned long pmsLastRead = 0;
struct PMS5003Data {
    uint16_t pm1_0_std, pm2_5_std, pm10_std;
    uint16_t pm1_0_atm, pm2_5_atm, pm10_atm;
    uint16_t particles_0_3um, particles_0_5um, particles_1_0um;
    uint16_t particles_2_5um, particles_5_0um, particles_10um;
};
PMS5003Data pmsData;
bool parsePMS() {
    while (pmsSerial.available()) {
        int b = pmsSerial.read();
        if (pmsIndex == 0 && b == 0x42) { pmsBuffer[pmsIndex++] = b; }
        else if (pmsIndex == 1 && b == 0x4D) { pmsBuffer[pmsIndex++] = b; }
        else if (pmsIndex >= 2 && pmsIndex < 32) { pmsBuffer[pmsIndex++] = b; }
        else { pmsIndex = 0; }
        if (pmsIndex == 32) {
            uint16_t len = pmsBuffer[2]*256 + pmsBuffer[3];
            if (len == 28) {
                uint16_t sum = 0;
                for (int i = 0; i < 30; i++) sum += pmsBuffer[i];
                uint16_t checksum = pmsBuffer[30]*256 + pmsBuffer[31];
                if (sum == checksum) {
                    pmsData.pm1_0_std  = pmsBuffer[4]*256 + pmsBuffer[5];
                    pmsData.pm2_5_std  = pmsBuffer[6]*256 + pmsBuffer[7];
                    pmsData.pm10_std   = pmsBuffer[8]*256 + pmsBuffer[9];
                    pmsData.pm1_0_atm  = pmsBuffer[10]*256 + pmsBuffer[11];
                    pmsData.pm2_5_atm  = pmsBuffer[12]*256 + pmsBuffer[13];
                    pmsData.pm10_atm   = pmsBuffer[14]*256 + pmsBuffer[15];
                    pmsData.particles_0_3um = pmsBuffer[16]*256 + pmsBuffer[17];
                    pmsData.particles_0_5um = pmsBuffer[18]*256 + pmsBuffer[19];
                    pmsData.particles_1_0um = pmsBuffer[20]*256 + pmsBuffer[21];
                    pmsData.particles_2_5um = pmsBuffer[22]*256 + pmsBuffer[23];
                    pmsData.particles_5_0um = pmsBuffer[24]*256 + pmsBuffer[25];
                    pmsData.particles_10um  = pmsBuffer[26]*256 + pmsBuffer[27];
                    pmsIndex = 0;
                    return true;
                }
            }
            pmsIndex = 0;
        }
    }
    return false;
}
#endif

#ifdef TEST_MQ2
float mq2Ro = 10.0;
float mq2ReadRS() {
    int raw = analogRead(MQ2_ANA_PIN);
    float v = raw * (3.3 / 4095.0);
    return (3.3 * RL_VALUE / v) - RL_VALUE;
}
float mq2Calibrate() {
    float val = 0.0;
    for (int i = 0; i < 500; i++) { val += mq2ReadRS(); delay(10); }
    return (val / 500.0) / RO_CLEAN_AIR_FACTOR;
}
unsigned long mq2LastRead = 0;
#endif

#ifdef TEST_VOLTAGE
const float AC_DIV_RATIO = (AC_R1 + AC_R2) / AC_R2;
const float UPS_DIV_RATIO = (UPS_R1 + UPS_R2) / UPS_R2;
unsigned long voltLastRead = 0;
#endif

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);

    Serial.println();
    Serial.println("################################################");
    Serial.println("#  AI-GUARDIAN - SENSOR TEST SUITE             #");
    Serial.println("#  ESP32 NodeMCU-32S - All Sensors             #");
    Serial.println("################################################");
    Serial.println();

#ifdef TEST_DHT11
    Serial.println("[1/8] DHT11 Setup...");
    dht.begin();
    delay(2000);
#endif

#ifdef TEST_PMS5003
    Serial.println("[2/8] PMS5003 Setup...");
    pmsSerial.begin(9600, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);
    delay(30000);
    unsigned char wakeup[] = {0x42,0x4D,0xE4,0x00,0x01,0x01,0x73};
    pmsSerial.write(wakeup, 7);
#endif

#ifdef TEST_MQ2
    Serial.println("[3/8] MQ-2 Setup...");
    pinMode(MQ2_D0_PIN, INPUT);
    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);
    Serial.println("    Calibrating MQ-2 (5 min)...");
    mq2Ro = mq2Calibrate();
    Serial.print("    Ro = "); Serial.print(mq2Ro); Serial.println(" kOhm");
#endif

#ifdef TEST_LEAK
    Serial.println("[4/8] Leak Sensor Setup...");
    pinMode(LEAK_PIN, INPUT);
    pinMode(LEAK_LED_PIN, OUTPUT);
    digitalWrite(LEAK_LED_PIN, LOW);
#endif

#ifdef TEST_ACS712
    Serial.println("[5/8] ACS712 Setup...");
    pinMode(ACS712_PIN, INPUT);
    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);
    delay(1000);
#endif

#ifdef TEST_PIR
    Serial.println("[6/8] HC-SR501 PIR Setup...");
    pinMode(PIR_PIN, INPUT);
    pinMode(PIR_LED_PIN, OUTPUT);
    digitalWrite(PIR_LED_PIN, LOW);
    delay(30000);
#endif

#ifdef TEST_REED
    Serial.println("[7/8] Reed Switch Setup...");
    pinMode(REED_PIN, INPUT_PULLUP);
#endif

#ifdef TEST_VOLTAGE
    Serial.println("[8/8] Voltage Divider Setup...");
    pinMode(AC_VOLTAGE_PIN, INPUT);
    pinMode(UPS_VOLTAGE_PIN, INPUT);
    analogSetAttenuation(ADC_11db);
    analogSetWidth(12);
#endif

    Serial.println();
    Serial.println("================================================");
    Serial.println("  TAT CA CAM BIEN DA KHOI TAO!");
    Serial.println("  Ket qua se hien thi lien tuc tren Serial Monitor");
    Serial.println("  Toc do: 115200 baud");
    Serial.println("================================================");
    Serial.println();
}

void loop() {
    unsigned long now = millis();

#ifdef TEST_DHT11
    if (now - dhtLastRead >= DHT_READ_INTERVAL) {
        dhtLastRead = now;
        float t = dht.readTemperature();
        float h = dht.readHumidity();
        if (!isnan(t) && !isnan(h)) {
            Serial.print("[DHT11] T="); Serial.print(t, 1); Serial.print("C H="); Serial.print(h, 1); Serial.println("%");
        }
    }
#endif

#ifdef TEST_PMS5003
    if (now - pmsLastRead >= PMS_READ_INTERVAL) {
        pmsLastRead = now;
        if (parsePMS()) {
            Serial.print("[PMS5003] PM2.5="); Serial.print(pmsData.pm2_5_std);
            Serial.print(" PM10="); Serial.println(pmsData.pm10_std);
        }
    }
#endif

#ifdef TEST_MQ2
    if (now - mq2LastRead >= 2000) {
        mq2LastRead = now;
        int raw = analogRead(MQ2_ANA_PIN);
        float rs = mq2ReadRS();
        float ratio = rs / mq2Ro;
        int digital = digitalRead(MQ2_D0_PIN);
        Serial.print("[MQ-2] ADC="); Serial.print(raw);
        Serial.print(" RS/RO="); Serial.print(ratio, 2);
        Serial.print(" D="); Serial.println(digital == HIGH ? "GAS!" : "OK");
    }
#endif

#ifdef TEST_LEAK
    int leak = digitalRead(LEAK_PIN);
    digitalWrite(LEAK_LED_PIN, leak == LOW ? HIGH : LOW);
    if (leak == LOW) {
        Serial.println("[LEAK] *** RO NUOC PHAT HIEN! ***");
    }
#endif

#ifdef TEST_ACS712
    static unsigned long acsLast = 0;
    if (now - acsLast >= 1000) {
        acsLast = now;
        int raw = analogRead(ACS712_PIN);
        float v = raw * (3.3 / 4095.0);
        float i = abs((v - 1.65) / ACS712_SENSITIVITY);
        Serial.print("[ACS712] V="); Serial.print(v, 3); Serial.print(" I="); Serial.print(i, 3); Serial.println("A");
    }
#endif

#ifdef TEST_PIR
    int pir = digitalRead(PIR_PIN);
    digitalWrite(PIR_LED_PIN, pir == HIGH ? HIGH : LOW);
    if (pir == HIGH) {
        Serial.println("[PIR] *** CHUYEN DONG PHAT HIEN! ***");
    }
#endif

#ifdef TEST_REED
    static bool lastReed = true;
    int reed = digitalRead(REED_PIN);
    if (reed != lastReed) {
        lastReed = reed;
        Serial.println(reed == HIGH ? "[REED] CUA MO!" : "[REED] CUA DONG!");
    }
#endif

#ifdef TEST_VOLTAGE
    if (now - voltLastRead >= 2000) {
        voltLastRead = now;
        int acRaw = analogRead(AC_VOLTAGE_PIN);
        int upsRaw = analogRead(UPS_VOLTAGE_PIN);
        float acV = (acRaw * (3.3/4095.0) * AC_DIV_RATIO / sqrt(2.0)) * AC_CALIBRATION;
        float upsV = (upsRaw * (3.3/4095.0) * UPS_DIV_RATIO) * UPS_CALIBRATION;
        Serial.print("[VOLT] AC="); Serial.print(acV, 1); Serial.print("V UPS="); Serial.print(upsV, 2); Serial.println("V");
    }
#endif

    delay(10);
}
