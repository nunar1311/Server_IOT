# AI-GUARDIAN - ESP32 SENSOR TEST SUITE

Thu muc chua cac bo test rieng le cho tung cam bien tren ESP32 NodeMCU-32S.

## CAU TRUC THU MUC

```
hardware/esp32_sensor_tests/
|
+--- config.h
|    Cau hinh chung: GPIO pins, nguong, thoi gian doc
|
+--- test_01_dht11/
|    +--- test_01_dht11.ino
|    Cam bien: DHT11 (Nhiet do / Do am)
|
+--- test_02_pms5003/
|    +--- test_02_pms5003.ino
|    Cam bien: PMS5003 (Bu PM2.5)
|
+--- test_03_mq2_gas/
|    +--- test_03_mq2_gas.ino
|    Cam bien: MQ-2 (Khoi / Gas)
|
+--- test_04_leak_sensor/
|    +--- test_04_leak_sensor.ino
|    Cam bien: Leak Sensor (Ro nuoc)
|
+--- test_05_acs712_current/
|    +--- test_05_acs712_current.ino
|    Cam bien: ACS712 30A (Ro dien)
|
+--- test_06_hcsr501_pir/
|    +--- test_06_hcsr501_pir.ino
|    Cam bien: HC-SR501 (Chuyen dong)
|
+--- test_07_reed_switch/
|    +--- test_07_reed_switch.ino
|    Cam bien: Reed Switch (Cua mo)
|
+--- test_08_09_voltage_divider/
|    +--- test_08_09_voltage_divider.ino
|    Cam bien: Voltage Divider (Dien ap AC & UPS)
|
|+--- test_10_oled/
|    +--- test_10_oled.ino
|    +--- config.h
|    Cam bien: OLED 1.3" SH1106 I2C
|
+--- master_test_all_sensors/
|    +--- master_test_all_sensors.ino
|    Test tat ca cam bien cung luc
|
+--- README.md
     Huong dan su dung
```

## CHI TIET CAM BIEN

| STT | Cam bien | Model | Chan GPIO | Loai | Dien ap |
|-----|----------|-------|-----------|------|---------|
| 1 | Nhiet do/Do am | DHT11 | IO32 | Digital | 3.3V/5V |
| 2 | Bu PM2.5 | PMS5003 | TX2=IO17, RX2=IO16 | UART | 5V |
| 3 | Khoi/Gas | MQ-2 | IO33 | Analog | 5V |
| 4 | Roan Nuoc | Leak Sensor | IO34 | Digital | 3.3V |
| 5 | Roan Dien | ACS712 (30A) | IO35 | Analog | 5V |
| 6 | Chuyen Dong | HC-SR501 | IO26 | Digital | 5V |
| 7 | Cua Mo | Reed Switch | IO27 | Digital | 3.3V |
| 8 | Dien ap AC | Voltage Divider | IO36 | Analog | 5V |
| 9 | Dien ap UPS | Voltage Divider | IO39 | Analog | 5V |
| 10 | Man hinh OLED | SH1106 1.3" | IO21(SDA)/IO22(SCL) | I2C | 3.3V |

## HUONG DAN SU DUNG

### Buoc 1: Cau hinh Wifi va MQTT

Mo file `config.h`, sua cac gia tri:

```cpp
#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"
#define MQTT_SERVER "192.168.1.100"
#define MQTT_PORT 1883
```

### Buoc 2: Them thu vien Arduino

Cai dat cac thu vien sau tu Library Manager:

| Thu vien | Ten trong Library Manager |
|----------|---------------------------|
| DHT sensor library | Adafruit DHT Sensor |
| JSON | ArduinoJson |
| Adafruit GFX | Adafruit GFX Library |
| Adafruit SH110X | Adafruit SH110X |

### Buoc 3: Tai file test len ESP32

1. Mo Arduino IDE
2. File > Open > Chon file `.ino` trong folder test tuong ung
3. Tools > Board > ESP32 Dev Module
4. Tools > Upload Speed > 115200
5. Upload

### Buoc 4: Mo Serial Monitor

Tools > Serial Monitor, toc do 115200 baud.

## CHI TIET TUNG CAM BIEN

### Test 01 - DHT11 (Nhiet do / Do am)

**Mach noi:**
- VCC -> 3.3V hoac 5V
- GND -> GND
- Data -> IO32

**Thong so ky thuat:**
- Nhiet do: 0-50*C (chinh xac ±2*C)
- Do am: 20-90%RH (chinh xac ±5%RH)
- Tan so doc: moi 2 giay

**Ket qua mong muon:**
```
--- DHT11 Data ---
Nhiet do:   25.0 *C | 77.0 *F
Do am:      65.0 %
Heat Index: 77.0 *F
```

### Test 02 - PMS5003 (Bu PM2.5)

**Mach noi:**
- VCC -> 5V
- GND -> GND
- TX -> IO17 (RX2)
- RX -> IO16 (TX2)

**Thong so ky thuat:**
- Pho bien: 0-500 ug/m3
- Do phan giai: 1 ug/m3
- Tan so doc: moi 1 giay

**Luu y:**
- Lan dau su dung can cho 30 giay de on dinh
- PMS5003 can che do Active (khong phai Passive)

**Ket qua mong muon:**
```
--- PMS5003 Data ---
PM1.0:  12
PM2.5:  25 ug/m3
PM10:   35 ug/m3
```

**Bang chat luong khong khi (PM2.5):**

| PM2.5 (ug/m3) | Chat luong |
|---------------|------------|
| 0-12 | Tot |
| 12.1-35.4 | Trung binh |
| 35.5-55.4 | Khong tot |
| 55.5-150.4 | Xau |
| 150.5+ | Nguy hiem |

### Test 03 - MQ-2 (Khoi / Gas)

**Mach noi:**
- VCC -> 5V
- GND -> GND
- A0 -> IO33 (Analog)
- D0 -> IO4 (Digital - tuy chon)

**Thong so ky thuat:**
- Dien ap hoat dong: 5V
- Cong suat: 750mW
- Khoang do: LPG, CO, Smoke, H2, CH4, Alcohol
- Tan so doc: moi 500ms

**Luu y quan trong:**
- MQ-2 can 24-48h de doi lan dau (burn-in)
- Preheat 5-10 phut truoc khi su dung
- Chuc nang calibrate tu dong khi khoi dong
- Dat o vi tri thong gio, tranh bui

**Calibration (neu can):**
```cpp
// Neu gia tri RS/RO o khong khi sach nho hon 0.9
// Sua gia tri RO_CLEAN_AIR_FACTOR trong config.h
// Gia tri mac dinh: 9.83
```

**Ket qua mong muon (khong khi sach):**
```
--- MQ-2 Data ---
ADC Raw:    ~150-300
Voltage:    ~0.12-0.24 V
RS:         ~15-30 kOhm
RS/RO:      ~0.9-2.0

--- Nong do (ppm) ---
LPG:        0-100 ppm
CO:         0-50 ppm
Smoke:      0-100 ppm
```

### Test 04 - Leak Sensor (Ro nuoc)

**Mach noi:**
- VCC -> 3.3V
- GND -> GND
- Signal -> IO34

**LED Indicator:**
- IO2 -> LED (bat khi co ro nuoc)

**Thong so ky thuat:**
- Dien ap: 3.3V
- Dong dien: <10mA
- Do dai day: 30cm (co the keo dai)

**Luu y:**
- Cam bien phat hien nuoc cham vao 2 day kim loai
- Tro ve HIGH khi co nuoc, LOW khi khong co
- Co the dung day dam bao 2 day khong cham nhau

**Cach test:**
1. De 2 day cam bien khong cham nhau -> LED tat
2. Nhог nuoc vao 2 day -> LED bat
3. Lau khô -> LED tat

### Test 05 - ACS712 (Ro dien)

**Mach noi:**
- VCC -> 5V
- GND -> GND
- OUT -> IO35

**Thong so ky thuat (model 30A):**
- Dong dien max: 30A AC
- Sensitivity: 66mV/A
- Diem 0 (khong tai): 2.5V (50% VCC)
- Do chinh xac: ±1.5% tai nhiet do phong

**Luu y quan trong:**
- NOI DUNG: Cat nguon truoc khi noi day
- Gioi han dong dien: Khong qua 30A lien tuc
- Lam mat: Su dung heatsink neu can
- Can hieu chinh offset truoc khi su dung

**Cach noi day:**
1. Ngat nguon AC
2. Noi day AC qua chan IP+ va IP- cua ACS712
3. Dau vao tai (van dong hoac may bom)
4. Bat nguon va test

**Offset calibration:**
```
Neu ADC Voltage > 1.8V: Diem 0 dang cao hon 2.5V
Neu ADC Voltage < 1.5V: Diem 0 dang thap hon 2.5V
Muc tieu: 1.65V (chinh giua 0-3.3V)
```

**Ket qua mong muon (khong co tai):**
```
ADC Voltage:  ~1.65V (hoac gan 1.65V)
Dong dien AC: ~0.00 A
[OK] Khong co ro dien
```

### Test 06 - HC-SR501 (Chuyen dong)

**Mach noi:**
- VCC -> 5V
- GND -> GND
- OUT -> IO26

**LED Indicator:**
- IO25 -> LED (bat khi phat hien chuyen dong)

**Thong so ky thuat:**
- Dien ap: 5V
- Dong dien: <65mA
- Tam phat hien: 3-7m (dieu chinh duoc)
- Goc phat hien: <120 deg
- Thoi gian tre: 0.3s - 5min (dieu chinh bang bien tro)

**Luu y:**
- Cho 30s on dinh truoc khi test (calibration)
- 2 bien tro tren mach:
  - Sensitivity: Dieu chinh khoang cach (trai = xa, phai = gan)
  - Time Delay: Thoi gian output HIGH sau khi phat hien (trai = ngan, phai = dai)
- Khong dat gan nguon nhiet, quat, cua so

**Cach test:**
1. Cho 30s on dinh
2. Di chuyen truoc cam bien
3. LED se bat khi phat hien nguoi
4. LED tat sau thoi gian delay

**Ket qua mong muon:**
```
*** CHUYEN DONG PHAT HIEN! ***
Motion #1 | Thoi gian: 5s
CO NGUOI!
LED Indicator: BAT (Do)
Tong so lan phat hien: 1
```

### Test 07 - Reed Switch (Cua mo)

**Mach noi:**
- VCC -> 3.3V
- GND -> GND
- Signal -> IO27 (INPUT_PULLUP)

**Thong so ky thuat:**
- Dien ap: 3.3V
- Loai: Normally Open (NO) khi khong co nam cham
- Do dai gap: 15-20mm (tuy loai)
- Dong dien max: 0.5A

**Luu y:**
- Su dung INPUT_PULLUP trong code
- Nam cham gan = CUA DONG = Pin = LOW
- Nam cham xa = CUA MO = Pin = HIGH

**Cach test:**
1. Gap nam cham gan reed switch -> "DONG CUA"
2. Di chuyen nam cham ra xa -> "MO CUA"

**Ket qua mong muon:**
```
========================================
>>>  CUA MO RA!  <<<
Thoi gian mo: 120s
So lan mo: 3
========================================
--- Reed [125s] ---
Door State: [OPEN  ] | Pin=HIGH | Opens=3 | Closes=2
```

### Test 08 & 09 - Voltage Divider (Dien ap)

**Mach noi AC (IO36):**
```
    100k Ohm (R1)
---/\/\/\/---+---/\/\/\/--- 220V AC
             |
           10k Ohm (R2)
             |
            GND
             |
         ADC IO36
```
He so chia: (100k + 10k) / 10k = 11

**Mach noi UPS (IO39):**
```
    100k Ohm (R1)
---/\/\/\/---+---/\/\/\/--- 12V UPS
             |
           10k Ohm (R2)
             |
            GND
             |
         ADC IO39
```

**Luu y quan trong - NGUY HIEM DIEN AP CAO:**
- DIEN AP 220V NGUY HIEM! Co the gay chet!
- Su dung bien tro hoac mach cach ly
- Kiem tra ky mang cach dien truoc khi cham
- Neu co the, su dung AC-DC 5V module thay vi voltage divider truc tiep

**Calibration:**
```cpp
// Neu gia tri do duoc khac voi von ke, dieu chinh trong config.h:
// AC:  AC_CALIBRATION (mac dinh 1.0)
// UPS: UPS_CALIBRATION (mac dinh 1.0)

// Vi du: Neu do duoc 225V nhung von ke la 220V
// AC_CALIBRATION = 220.0 / 225.0 = 0.978
```

**Nguong canh bao:**
| Loai | Nguong thap | Nguong cao |
|------|-------------|------------|
| AC | 200V | 250V |
| UPS | 11V | 13.8V |

### Test 10 - OLED 1.3" SH1106 (Man hinh I2C)

**Mach noi:**
- VCC -> 3.3V
- GND -> GND
- SDA -> IO21
- SCL -> IO22

**LED Indicator (tuy chon):**
- IO4 -> LED (neu su dung)

**Thong so ky thuat:**
- Kich thuoc: 1.3 inch
- Do phan giai: 128x64 pixel
- Giao tiep: I2C
- Dia chi mac dinh: 0x3C
- Dien ap: 3.3V

**Luu y:**
- Su dung thu vien **Adafruit GFX** + **Adafruit SH110X**
- Neu man hinh trang, thu dia chi 0x3D
- Can delay 1-2 giay sau khi begin() de man hinh khoi dong
- Su dung display.display() de thuc su hien thi du lieu

**Ket qua mong muon:**
```
=== OLED TEST ===
1.3 inch SH1106 I2C
Counter: 1234
Uptime: 456s
Time: 00:07:36
```

## MASTER TEST - TEST TAT CA

File `master_test_all_sensors/master_test_all_sensors.ino` cho phep test nhieu cam bien cung luc.

**Cach su dung:**

1. Comment/Uncomment cac define o dau file de chon cam bien:
```cpp
#define TEST_DHT11      // Nhiet do / Do am
#define TEST_PMS5003    // Bu PM2.5
#define TEST_MQ2        // Khoi / Gas
#define TEST_LEAK       // Roan nuoc
#define TEST_ACS712     // Roan dien
#define TEST_PIR        // Chuyen dong
#define TEST_REED       // Cua mo
#define TEST_VOLTAGE    // Dien ap
#define TEST_OLED       // Man hinh OLED 1.3" SH1106 I2C
```

2. Tai len va kiem tra ket qua ngon ngu:
```
[DHT11] T=25.5C H=65.0%
[PMS5003] PM2.5=25 PM10=35
[MQ-2] ADC=250 RS/RO=1.5 D=OK
[LEAK] ...
[ACS712] V=1.652 I=0.030A
[PIR] ...
[REED] CUA DONG!
[VOLT] AC=220.5V UPS=12.3V
[OLED] Display update OK
```

## MAP GPIO CHI TIET

```
          ESP32 NodeMCU-32S
         ====================

              +-----------+
         EN  | 1       38 | GPIO0 (烧录模式)
         VP  | 2       37 | GPIO3 (TX0)
         VN  | 3       36 | GPIO1 (RX0)
    GPIO36  | 4       35 | GPIO22 | I2C SCL
    GPIO37  | 5       34 | GPIO21 | I2C SDA
    GPIO38  | 6       33 | GPIO19 | 
    GPIO18  | 7       32 | GPIO23 |
    GPIOGND | 8       31 | GPIOGND|
    GPIO5   | 9       30 | GPIO10 | SPI MOSI
    GPIO17* |10       29 | GPIO9  | SPI MISO (*PMS5003 TX)
    GPIO16* |11       28 | GPIO11 | SPI CS  (*PMS5003 RX)
    GPIO4   |12       27 | GPIO2  | LED (D4)
    GPIOGND |13       26 | GPIOGND|
    GPIOGND |14       25 | 3V3    |
    GPIO34+ |15       24 | GPIO35+| (*Leak, ACS712)
    GPIO39+ |16       23 | GPIO0  |
    GPIO36+ |17       22 | BAT    | (*AC Voltage)
    GPIO32  |18       21 | GND    |  (*DHT11)
    GPIO33  |19       20 | 5V     |
    GPIO25  |20       19 | 5V     |  (*PIR LED)
    GPIO26  |21       18 | GND    |  (*PIR)
    GPIO27  |22       17 | 3V3    |
    GPIONC  |23       16 | GND    |
    GPIO14  |24       15 | GPIO15 |
    GPIO12  |25       14 | GPIO13 |
    GND     |26       13 | GND    |
    VIN     |27       12 | GND    |

  * = Su dung cho cam bien
  + = INPUT ONLY chan (chi doc)
  * = UART cho PMS5003
```

## XU LY SAI LAM THUONG GAP

### DHT11 khong doc duoc

1. Kiem tra ket noi VCC, GND, Data
2. Kiem tra chan Data = IO32
3. Thu thay doi pullup 4.7k-10k ohm
4. Kiem tra Serial Monitor 115200 baud

### PMS5003 khong gui du lieu

1. Kiem tra RX/TX (lat nguoc = khong hoat dong)
2. Cho 30s de PMS5003 wake up
3. Kiem tra nguon 5V (PMS5003 can 5V)
4. Thu gui lenh wakeup thu cong

### MQ-2 cho gia tri bat thuong

1. MQ-2 can 24-48h de doi (lan dau)
2. Su dung sau 5-10 phut preheat
3. Kiem tra nguon 5V
4. Chuc nang calibrate tu dong se chay khi setup()

### ACS712 cho gia tri offset sai

1. Do dien ap o chan OUT khi khong co tai
2. Gia tri mong muon: 2.5V (neu VCC=5V) hoac 1.65V (neu VCC=3.3V)
3. Neu khac nhieu, co the cam bien bi hong

### HC-SR501 khong hoat dong

1. Cho 30s de cam bien on dinh
2. Kiem tra 2 bien tro:
   - Sensitivity (ben trai): xoay phai de tang
   - Time delay (ben phai): xoay trai de giam
3. Khong dat gan nguon nhiet, cua so, quat

### Voltage Divider gia tri sai

1. Tinh toan lai he so chia: R1/(R1+R2)
2. Kiem tra gia tri dien tro thuc te (co the chenh lech 5-10%)
3. Dieu chinh AC_CALIBRATION / UPS_CALIBRATION trong config.h

## THU VIEN CAN CAI DAT

| Thu vien | Nguon | Phien ban |
|----------|-------|-----------|
| DHT sensor library | Adafruit | >= 1.4.0 |
| ArduinoJson | ArduinoJson | >= 6.0 |
| Adafruit GFX | Adafruit | >= 1.10.0 |
| Adafruit SH110X | Adafruit | >= 2.0.0 |

Cai dat: Tools > Manage Libraries > Tim ten thu vien > Install

## TAC GIA & LICENSE

AI-Guardian Project - ESP32 Sensor Test Suite
Phat trien boi: AI-Guardian Team
