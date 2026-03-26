// ============================================================
// TEST 02: CAM BIEN PMS5003 - BUY PM2.5
// ============================================================
// Cam bien: PMS5003 (Plantower)
// Giao tiep: UART (TX2=IO17, RX2=IO16)
// Dien ap: 5V
// Thu vien: HardwareSerial (tich hop san)
// ============================================================

#include <Arduino.h>
#include <HardwareSerial.h>
#include "config.h"

HardwareSerial pmsSerial(2);

unsigned char pmsBuffer[32];
int pmsIndex = 0;
unsigned long lastReadTime = 0;

struct PMS5003Data {
    uint16_t pm1_0_std;
    uint16_t pm2_5_std;
    uint16_t pm10_std;
    uint16_t pm1_0_atm;
    uint16_t pm2_5_atm;
    uint16_t pm10_atm;
    uint16_t particles_0_3um;
    uint16_t particles_0_5um;
    uint16_t particles_1_0um;
    uint16_t particles_2_5um;
    uint16_t particles_5_0um;
    uint16_t particles_10um;
};

PMS5003Data pmsData;
bool pmsDataReady = false;

void pmsSetup() {
    Serial.println("=== TEST 02: PMS5003 (Bu PM2.5) ===");
    Serial.print("TX Pin: IO"); Serial.println(PMS_TX_PIN);
    Serial.print("RX Pin: IO"); Serial.println(PMS_RX_PIN);
    Serial.println("Khoi tao UART...");

    pmsSerial.begin(9600, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);

    Serial.println("Cho 30s de cam bien on dinh (lan dau canh SAT mode)...");
    delay(30000);

    // Wakeup command
    unsigned char wakeup[] = {0x42, 0x4D, 0xE4, 0x00, 0x01, 0x01, 0x73 };
    pmsSerial.write(wakeup, 7);
    delay(1000);

    Serial.println("[OK] PMS5003 khoi tao xong!");
    Serial.println();
}

bool parsePMS5003() {
    while (pmsSerial.available()) {
        int b = pmsSerial.read();
        if (pmsIndex == 0 && b == 0x42) {
            pmsBuffer[pmsIndex++] = b;
        } else if (pmsIndex == 1 && b == 0x4D) {
            pmsBuffer[pmsIndex++] = b;
        } else if (pmsIndex >= 2 && pmsIndex < 32) {
            pmsBuffer[pmsIndex++] = b;
        } else {
            pmsIndex = 0;
        }

        if (pmsIndex == 32) {
            uint16_t len = pmsBuffer[2] * 256 + pmsBuffer[3];
            if (len == 28) {
                uint16_t sum = 0;
                for (int i = 0; i < 30; i++) sum += pmsBuffer[i];
                uint16_t checksum = pmsBuffer[30] * 256 + pmsBuffer[31];
                if (sum == checksum) {
                    pmsData.pm1_0_std    = pmsBuffer[4]  * 256 + pmsBuffer[5];
                    pmsData.pm2_5_std    = pmsBuffer[6]  * 256 + pmsBuffer[7];
                    pmsData.pm10_std     = pmsBuffer[8]  * 256 + pmsBuffer[9];
                    pmsData.pm1_0_atm    = pmsBuffer[10] * 256 + pmsBuffer[11];
                    pmsData.pm2_5_atm    = pmsBuffer[12] * 256 + pmsBuffer[13];
                    pmsData.pm10_atm     = pmsBuffer[14] * 256 + pmsBuffer[15];
                    pmsData.particles_0_3um = pmsBuffer[16] * 256 + pmsBuffer[17];
                    pmsData.particles_0_5um = pmsBuffer[18] * 256 + pmsBuffer[19];
                    pmsData.particles_1_0um = pmsBuffer[20] * 256 + pmsBuffer[21];
                    pmsData.particles_2_5um = pmsBuffer[22] * 256 + pmsBuffer[23];
                    pmsData.particles_5_0um = pmsBuffer[24] * 256 + pmsBuffer[25];
                    pmsData.particles_10um  = pmsBuffer[26] * 256 + pmsBuffer[27];
                    pmsIndex = 0;
                    return true;
                } else {
                    Serial.println("[LOI] PMS5003 checksum khong khop!");
                }
            }
            pmsIndex = 0;
        }
    }
    return false;
}

void pmsLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= PMS_READ_INTERVAL) {
        lastReadTime = now;

        if (parsePMS5003()) {
            Serial.println("--- PMS5003 Data ---");
            Serial.println("=== Kich thuoc hat theo tieu chuan (ug/m3) ===");
            Serial.print("PM1.0:  "); Serial.println(pmsData.pm1_0_std);
            Serial.print("PM2.5:  "); Serial.print(pmsData.pm2_5_std);
            if (pmsData.pm2_5_std > PM25_MAX) {
                Serial.println(" ug/m3 [CANH BAO: Vuot nguong!]");
            } else {
                Serial.println(" ug/m3");
            }
            Serial.print("PM10:   "); Serial.println(pmsData.pm10_std);

            Serial.println("=== Kich thuoc hat theo moi truong (ug/m3) ===");
            Serial.print("PM1.0:  "); Serial.println(pmsData.pm1_0_atm);
            Serial.print("PM2.5:  "); Serial.println(pmsData.pm2_5_atm);
            Serial.print("PM10:   "); Serial.println(pmsData.pm10_atm);

            Serial.println("=== So hat phan tich duoc ===");
            Serial.print("0.3um:  "); Serial.println(pmsData.particles_0_3um);
            Serial.print("0.5um:  "); Serial.println(pmsData.particles_0_5um);
            Serial.print("1.0um:  "); Serial.println(pmsData.particles_1_0um);
            Serial.print("2.5um:  "); Serial.println(pmsData.particles_2_5um);
            Serial.print("5.0um:  "); Serial.println(pmsData.particles_5_0um);
            Serial.print("10um:   "); Serial.println(pmsData.particles_10um);

            Serial.println();
        } else {
            Serial.println("[CHO] Dang cho du lieu PMS5003...");
        }
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    pmsSetup();
}

void loop() {
    pmsLoop();
}
