// ============================================================
// TEST 07: REED SWITCH - CAM BIEN CUA MO
// ============================================================
// Cam bien: Reed Switch (Nam cham)
// Chan GPIO: IO27 (INPUT PULLUP)
// Dien ap: 3.3V
// Dac diem: Phat hien cua mo/ dong dua tren truong nam cham
// Mo cua = nam cham ra xa = reed switch OPEN = HIGH
// Dong cua = nam cham gan = reed switch CLOSED = LOW
// ============================================================

#include <Arduino.h>
#include "config.h"

enum DoorState {
    DOOR_CLOSED,
    DOOR_OPEN
};

DoorState currentDoorState = DOOR_CLOSED;
DoorState lastDoorState = DOOR_CLOSED;
unsigned long doorOpenStartTime = 0;
unsigned long lastReadTime = 0;
unsigned long openCount = 0;
unsigned long closeCount = 0;
unsigned long totalOpenTime = 0;
bool doorOpenLogged = false;

void reedSetup() {
    Serial.println("=== TEST 07: Reed Switch (Cua Mo) ===");
    Serial.print("Reed Pin: IO"); Serial.println(REED_PIN);
    Serial.println();
    Serial.println("Mo/Cua cua ban gap nam cham vao cam bien de test!");
    Serial.println("Dong cua (nam cham gan) -> State: CLOSED");
    Serial.println("Mo cua (nam cham xa)   -> State: OPEN");
    Serial.println();

    pinMode(REED_PIN, INPUT_PULLUP);

    delay(1000);

    int initialState = digitalRead(REED_PIN);
    currentDoorState = (initialState == LOW) ? DOOR_CLOSED : DOOR_OPEN;
    lastDoorState = currentDoorState;

    Serial.print("Trang thai khoi tao: ");
    Serial.println(currentDoorState == DOOR_CLOSED ? "DONG CUA" : "MO CUA");
    Serial.println();
}

const char* doorStateToString(DoorState state) {
    return state == DOOR_CLOSED ? "DONG" : "MO ";
}

void reedLoop() {
    unsigned long now = millis();
    if (now - lastReadTime >= 500) {
        lastReadTime = now;

        int reedValue = digitalRead(REED_PIN);
        currentDoorState = (reedValue == LOW) ? DOOR_CLOSED : DOOR_OPEN;

        unsigned long uptime = now / 1000;

        if (currentDoorState != lastDoorState) {
            if (currentDoorState == DOOR_OPEN) {
                doorOpenStartTime = now;
                openCount++;
                Serial.println("========================================");
                Serial.println(">>>  CUA MO RA!  <<<");
                Serial.print("Thoi gian mo: "); Serial.print(doorOpenStartTime / 1000); Serial.println("s");
                Serial.print("So lan mo: "); Serial.println(openCount);
                Serial.println("========================================");
            } else {
                unsigned long openDuration = (now - doorOpenStartTime) / 1000;
                closeCount++;
                totalOpenTime += openDuration;
                Serial.println("========================================");
                Serial.print(">>>  CUA DONG LAI!  <<<");
                Serial.print(" | Thoi gian mo: "); Serial.print(openDuration); Serial.println("s");
                Serial.print("Tong thoi gian mo: "); Serial.print(totalOpenTime / 60); Serial.println(" phut");
                Serial.print("So lan dong: "); Serial.println(closeCount);
                Serial.println("========================================");
            }
            lastDoorState = currentDoorState;
        }

        Serial.print("--- Reed ["); Serial.print(uptime); Serial.println("s] ---");
        Serial.print("Door State: [");
        Serial.print(currentDoorState == DOOR_CLOSED ? "CLOSED" : "OPEN  ");
        Serial.print("] | Pin="); Serial.print(reedValue == LOW ? "LOW" : "HIGH");
        Serial.print(" | Opens="); Serial.print(openCount);
        Serial.print(" | Closes="); Serial.print(closeCount);

        if (currentDoorState == DOOR_OPEN) {
            unsigned long currentOpenDuration = (now - doorOpenStartTime) / 1000;
            Serial.print(" | Open Time="); Serial.print(currentOpenDuration); Serial.println("s");
        } else {
            Serial.println();
        }

        if (currentDoorState == DOOR_OPEN && !doorOpenLogged) {
            Serial.println("[CANH BAO] Cua dang mo! Kiem tra an ninh!");
            doorOpenLogged = true;
        } else if (currentDoorState == DOOR_CLOSED) {
            doorOpenLogged = false;
        }

        Serial.println();
    }
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(500);
    reedSetup();
}

void loop() {
    reedLoop();
}
