# AI-Guardian - Hardware Setup Guide

## Muc luc

1. [Danh sach linh kien](#danh-sach-linh-kien)
2. [Cac buoc lap rap](#cac-buoc-lap-rap)
3. [Cau hinh WiFi](#cau-hinh-wifi)
4. [Cau hinh MQTT](#cau-hinh-mqtt)
5. [Kiem tra](#kiem-tra)
6. [Huong dan xu ly su co](#huong-dan-xu-ly-su-co)

---

## Danh sach linh kien

| STT | Linh kien | Model | So luong | Chi phi uoc tinh | Ghi chu |
|-----|----------|-------|----------|------------------|---------|
| 1 | Nhiet do/Do am | **DHT11** | 2 | 15K VND | Chuan do 2C (neu can chinh xac hon dung DHT22) |
| 2 | Cam bien bu | PMS5003 | 1 | 180K VND | PM1.0/2.5/10 |
| 3 | Cam bien khoi | MQ-2 | 1 | 25K VND | LPG, CO, Smoke |
| 4 | Day cam bien ro nuoc | Leak Cable | 2m | 80K VND | Chieu dai tuy chon |
| 5 | Cam bien dong dien | ACS712 (30A) | 1 | 45K VND | Phat hien ro dien |
| 6 | Cam bien chuyen dong | HC-SR501 | 2 | 30K VND | PIR |
| 7 | Cong tac trao cua | Reed Switch | 2 | 10K VND | + Magnet |
| 8 | Relay 8 kenh | 5V/10A | 1 | 90K VND | Optocoupler |
| 9 | ESP32-CAM | AI Thinker | 1 | 120K VND | Camera AI |
| 10 | Nguon 5V/10A | Adapter | 1 | 80K VND | Nuoc relay |
| 11 | Day dien, breadboard | Bộ | 1 | 100K VND | |
| 12 | UPS Mini | 12V/7Ah | 1 | 300K VND | Nguon du phong |
| **TONG** | | | | **~1,090K VND** | Chua co ESP32 & Pico (da co) |

---

## Kiem tra hardware

### ESP32 NodeMCU-32S CH340

```
Dau hieu nhan biet ESP32 NodeMCU-32S CH340:
- Chip USB: CH340 (neu la CP2102 thi la version khac)
- So chan: 30 pins
- Module: ESP-WROOM-32 (label tren chip)
- Nut boot: Co nut IO0 ben trai
- LED: IO2 thuong co LED xanh ben board
- Day cam: Micro USB

Kiem tra driver CH340 (Windows):
1. Cam ESP32 vao USB
2. Mo Device Manager (Win+X -> Device Manager)
3. Tim muc "Ports (COM & LPT)"
4. Nen thay "USB-Enhanced-SERIAL CH340" voi COMxx
5. Neu khong co, tai driver tai: https://www.wch-ic.com/downloads/CH341SER_ZIP.html
```

### Raspberry Pi Pico RP2040

```
Dau hieu nhan biet Pico RP2040:
- Chip chinh: RP2040 (label nho tren chip lon)
- Bo nho: 2MB QSPI Flash (ben sau board)
- So chan: 40 pins
- Onboard LED: GP25 (xanh duong, co san)
- Nut BOOTSEL: Ben trai cong USB
- Cong: Micro USB
```

---

## Cac buoc lap rap

### Buoc 1: Lap rap ESP32 NodeMCU-32S Sensor Node

**Luu y quan trong ve GPIO:**
- IO34, IO35, IO36, IO39: Chi INPUT ONLY (khong co pull-up/pull-down noi)
- IO32, IO33: Co pull-down noi san
- UART2 (IO16/IO17): Dung cho PMS5003
- I2C (IO21/IO22): Dung giao tiep I2C voi Pico

1. **Lap board ESP32 NodeMCU-32S** len dinh tray
2. **Noi DHT11**:
   - VCC -> 3.3V
   - GND -> GND
   - Data -> IO32
   - + 10K resistor giua Data va 3.3V (pull-up)
3. **Noi PMS5003** (UART2):
   - VCC -> 5V
   - GND -> GND
   - TX -> IO16 (RX2)
   - RX -> IO17 (TX2)
4. **Noi MQ-2**:
   - VCC -> 5V
   - GND -> GND
   - A0 -> IO33 (qua voltage divider 10K)
5. **Noi Leak Sensor**:
   - VCC -> 3.3V
   - GND -> GND
   - D0 -> IO34 (INPUT ONLY, Active LOW, 10K pull-up)
6. **Noi ACS712**:
   - VCC -> 5V
   - GND -> GND
   - OUT -> IO35 (INPUT ONLY, qua voltage divider)
7. **Noi HC-SR501**:
   - VCC -> 5V
   - GND -> GND
   - OUT -> IO26
   - Dat jumper sang H (kich hoat lien tuc)
8. **Noi Reed Switch**:
   - 1 chan -> IO27
   - 1 chan -> 3.3V (qua 10K pull-up)
   - Magnet gan cua
9. **Noi Voltage Dividers**:
   - Input voltage AC: 100K + 10K divider -> IO36 (INPUT ONLY)
   - UPS voltage: 20K + 10K divider -> IO39 (INPUT ONLY)
10. **Noi I2C (Pico)**:
    - ESP32 IO21 (SDA) -> Pico GP16
    - ESP32 IO22 (SCL) -> Pico GP17
    - Pull-up 4.7K keo len 3.3V

### Buoc 2: Lap rap Pico RP2040 Actuator

1. **Lap Pico len prototype board**
2. **Ket noi relay module**:
   - VCC -> 5V nguon rieng (QUAN TRONG - khong lay tu Pico!)
   - GND -> GND chung
   - IN1 -> GP0
   - IN2 -> GP1
   - IN3 -> GP2
   - IN4 -> GP3
   - IN5 -> GP4
   - IN6 -> GP5
   - IN7 -> GP6
   - IN8 -> GP7
3. **Ket noi I2C (ESP32)**:
   - Pico GP16 (SDA) -> ESP32 IO21
   - Pico GP17 (SCL) -> ESP32 IO22
   - Pull-up 4.7K keo len 3.3V
4. **Ket noi Buzzer** (optional):
   - Buzzer (+) -> GP15 (PWM)
   - Buzzer (-) -> GND

### Buoc 3: Lap rap nguon

1. **Lap rap bo nguon 5V/10A** cho relay (TACH RIENG)
2. **Ket noi UPS** 12V cho:
   - ESP32 (qua USB 5V)
   - Pico (VSYS 5V)
   - WiFi Router
   - Camera
3. **Lap rap Circuit Breaker** 20A cho mach 220V
4. **Lap rap GFCI/RCD** de phat hien ro dien

### Buoc 4: Lap rap UPS

1. **Ket noi UPS** vao mach 220V
2. **Ket noi** tat ca thiet bi can du phong
3. **Lap rap cam bien dien ap** UPS vao ESP32

---

## Cau hinh WiFi

### Tren ESP32

Chinh sua `config.h`:

```cpp
#define WIFI_SSID     "Ten_WiFi_Cua_Ban"
#define WIFI_PASSWORD "Mat_Khau_WiFi"
```

### Tren ESP32-CAM

Chinh sua dau file:

```cpp
#define WIFI_SSID     "Ten_WiFi_Cua_Ban"
#define WIFI_PASSWORD "Mat_Khau_WiFi"
```

### Tren Pico (neu co WiFi)

```python
WIFI_SSID = "Ten_WiFi_Cua_Ban"
WIFI_PASSWORD = "Mat_Khau_WiFi"
```

---

## Cau hinh MQTT

### Tren Mosquitto

Tao file `data/pwfile.conf`:

```bash
# Chay lenh nay de tao user
docker exec -it ai_guardian_mqtt mosquitto_passwd -c /mosquitto/config/pwfile.conf mqtt_user
# Nhap mat khau: mqtt_password
```

### Tren ESP32

```cpp
#define MQTT_SERVER   "192.168.1.100"  // IP may chu
#define MQTT_PORT     1883
```

### Tren Pico

```python
MQTT_BROKER = "192.168.1.100"  # IP may chu
MQTT_PORT    = 1883
MQTT_USER    = "mqtt_user"
MQTT_PASS    = "mqtt_password"
```

### Tren Backend

```python
MONGODB_URL = "mongodb://admin:ai_guardian_secure_pass_2024@localhost:27017"
# hoac
import os
os.environ["MONGODB_URL"] = "mongodb://admin:YOUR_PASSWORD@YOUR_IP:27017"
```

---

## Kiem tra

### Kiem tra tung cam bien

```cpp
// Them vao setup()
Serial.println("Testing sensors...");
Serial.printf("DHT11 Temp: %.1f C\n", dht.readTemperature());
Serial.printf("MQ-2 Gas: %d\n", analogRead(GPIO33));
Serial.printf("Motion: %d\n", digitalRead(GPIO26));
```

### Kiem tra relay

```python
from machine import Pin
relay = Pin(0, Pin.OUT)
relay.value(1)  # Bat relay
relay.value(0)  # Tat relay
```

### Kiem tra MQTT

```bash
# Subscribe topic
mosquitto_sub -h localhost -t "ai-guardian/#" -v

# Publish test message
mosquitto_pub -h localhost -t "ai-guardian/actions" -m '{"action":"fire","priority":"critical"}'
```

### Kiem tra MongoDB

```bash
# Kiem tra container
docker ps | grep ai_guardian

# Kiem tra logs
docker-compose logs mongodb

# Ket noi MongoDB shell
docker exec -it ai_guardian_mongo mongosh -u admin -p
# Mat khau: ai_guardian_secure_pass_2024
```

---

## Huong dan xu ly su co

### ESP32 khong ket noi WiFi

1. Kiem tra SSID va mat khau
2. Kiem tra router co hoat dong
3. Thu reset ESP32
4. Kiem tra khoang cach (nen < 10m)

### ESP32 khong ket noi MQTT

1. Kiem tra MQTT broker co chay khong: `docker ps | grep mosquitto`
2. Kiem tra IP MQTT trong code
3. Kiem tra firewall chan port 1883

### Pico khong nhan duoc lenh

1. Kiem tra MQTT connection: `print(mqtt_client.is_connected())`
2. Kiem tra relay module co nguon 5V rieng
3. Kiem tra GPIO da dung dung

### Cam bien cho gia tri sai

1. DHT11: Dung thu vien DHT, doi 2s de on dinh sau khi khoi dong
2. MQ-2: Chay 24h de kich hoat (burn-in)
3. PMS5003: Kiem tra quat co quay khong
4. ACS712: Hieu chinh offset (0A = 1.65V)

### Relay khong hoat dong

1. Kiem tra nguon 5V/10A co du khong
2. Kiem tra relay module co nhan tin hieu (LED chi sang)
3. Kiem tra transistor driver tren relay module
4. Do dien tro cuon day relay (~150-200 ohm)

---

## Bao tri dinh ky

| Tan suat | Cong viec | Ghi chu |
|----------|-----------|---------|
| Hang ngay | Kiem tra dashboard | Xem co bat thuong |
| Hang tuan | Kiem tra UPS | Dac biet sau khi mat dien |
| Hang thang | Ve sinh cam bien | Nei bot, bui |
| Hang quy | Hieu chinh cam bien | DHT11/DHT22, MQ-2 |
| Hang nam | Thay acquy UPS | Acqui 12V/7Ah |
