# AI-Guardian - So do noi day chi tiet

## Muc luc

- [Tong quan](#tong-quan)
- [Kiem tra hardware](#kiem-tra-hardware)
- [Ket noi ESP32 NodeMCU-32S - Cam bien](#ket-noi-esp32-nodemcu-32s---cam-bien)
- [Ket noi Pico RP2040 - Relay](#ket-noi-pico-rp2040---relay)
- [So do nguon](#so-do-nguon)
- [Ket noi UPS](#ket-noi-ups)
- [Ket noi Camera AI](#ket-noi-camera-ai)
- [Bang noi day chi tiet](#bang-noi-day-chi-tiet)

---

## Tong quan

He thong gom 3 tang chinh:

```
[ESP32 Sensor Node] <--MQTT/WiFi--> [Gateway/Server] <--MQTT/WiFi--> [Pico Actuator]
        |                                     |
   Cam bien (8)                           Mosquitto
                                          MongoDB
                                         FastAPI AI
                                              |
                                         Web Dashboard
```

**Hardware cua ban:**
- **ESP32 MCU**: NodeMCU-32S CH340 (ESP-WROOM-32, 30 pins)
- **Actuator MCU**: Raspberry Pi Pico RP2040 (40 pins)
- **USB Driver**: CH340 (Windows tu dong nhan, neu co van de tai: https://www.wch-ic.com/downloads/CH341SER_ZIP.html)

---

## Kiem tra hardware

### ESP32 NodeMCU-32S CH340 - Dac diem nhan dien

```
Dau hieu nhan biet ESP32 NodeMCU-32S CH340:
- Chip USB: CH340 (neu la CP2102 thi la version khac, van tuong thich)
- So chan: 30 pins
- Module: ESP-WROOM-32 (label tren chip)
- Nut boot: Co nut IO0 ben trai (gian giut de vao che do flash)
- LED: IO2 thuong co LED xanh ben board (nhap nhay khi nap code)
- Day cam: Micro USB
- Anten: Co anten PCB hoac IPEX
```

**So do chan (luoi phia tren):**

```
            +-------------------------------------------------------+
            |  ESP32 NodeMCU-32S (ESP-WROOM-32)        [_USB_]       |
            |  CH340 USB-UART                               [EN]     |
  3V3  --- |  [GND] [VIN/5V] [3V3] [IO0] [IO2]                |
  GND   --- |--------------------------------------------------|
  IO35* --- |  GND  TX0  RX0  IO1  IO3  IO21  IO22  TX2  RX2  IO19 |
            |------------------------------------------------------|
  IO34* --- |  IO34  IO35  IO32  IO33  IO25  IO26  IO27  I14  IO12 |
            |------------------------------------------------------|
  IO39* --- |  IO35* IO34* IO39* IO36* IO4   IO2   IO15  IO13  GND   |
  IO36* --- +------------------------------------------------------+
               INPUT ONLY    ADC1         ADC2

* GPIO34, GPIO35, GPIO36, GPIO39 chi INPUT ONLY
```

**GPIO Mapping chi tiet cho ESP32 NodeMCU-32S:**

| GPIO | Chuc nang               | ADC  | Uart | PWM  | Su dung trong he thong        |
|------|------------------------|------|------|------|-------------------------------|
| IO0  | Boot/JTAG              | -    | -    | Yes  | Nut boot (nap code)           |
| IO1  | TX0                    | -    | U0TX | Yes  | Debug/Flash (tranh dung)      |
| IO2  | LED onboard            | Yes  | -    | Yes  | Onboard LED (nhap nhay)       |
| IO3  | RX0                    | -    | U0RX | Yes  | Debug/Flash (tranh dung)      |
| IO4  | GPIO                   | Yes  | -    | Yes  | Optional                      |
| IO5  | GPIO                   | Yes  | -    | Yes  | Optional                      |
| IO12 | GPIO (J16)             | Yes  | -    | Yes  | Optional, JTAG-TDO            |
| IO13 | GPIO (J13)             | Yes  | -    | Yes  | Optional, JTAG-TDI            |
| IO14 | GPIO (J14)             | Yes  | -    | Yes  | Optional, JTAG-TMS            |
| IO15 | GPIO (J15)             | Yes  | -    | Yes  | Optional, JTAG-TCK           |
| IO16 | GPIO / UART2 RX        | Yes  | U2RX | Yes  | PMS5003 RX (UART2)           |
| IO17 | GPIO / UART2 TX        | Yes  | U2TX | Yes  | PMS5003 TX (UART2)           |
| IO18 | GPIO / HSPI CLK        | -    | -    | Yes  | SPI (VSPI)                    |
| IO19 | GPIO / HSPI MISO       | -    | -    | Yes  | SPI (VSPI)                    |
| IO21 | **I2C SDA**           | -    | -    | Yes  | **I2C giao tiep Pico**       |
| IO22 | **I2C SCL**           | -    | -    | Yes  | **I2C giao tiep Pico**       |
| IO23 | GPIO / HSPI MOSI       | -    | -    | Yes  | SPI (VSPI)                    |
| IO25 | GPIO (DAC1)            | Yes  | -    | Yes  | Optional                      |
| IO26 | **PIR Motion**         | Yes  | -    | Yes  | **HC-SR501 OUT**              |
| IO27 | **Reed Switch Door**   | Yes  | -    | Yes  | **Door sensor**               |
| IO32 | **DHT11 Temp/Hum**    | Yes  | -    | Yes  | **DHT11 Data**                |
| IO33 | **MQ-2 Gas/Smoke**    | Yes  | -    | Yes  | **MQ-2 A0 (analog)**          |
| IO34 | **Leak Sensor**        | Yes  | -    | No   | **INPUT ONLY - Leak D0**      |
| IO35 | **ACS712 Current**    | Yes  | -    | No   | **INPUT ONLY - Current**      |
| IO36 | **Voltage AC**         | Yes  | -    | No   | **INPUT ONLY - AC voltage**   |
| IO39 | **Voltage UPS**        | Yes  | -    | No   | **INPUT ONLY - UPS voltage**   |

### Raspberry Pi Pico RP2040 - Dac diem nhan dien

```
Dau hieu nhan biet Pico RP2040:
- Chip chinh: RP2040 (label nho tren chip lon)
- Bo nho: 2MB QSPI Flash (ben sau board)
- So chan: 40 pins
- Onboard LED: GP25 (xanh duong, co san)
- Nut BOOTSEL: Ben trai cong USB (gian giut de nap code)
- Cong: Micro USB
- Chip USB: Giua board
```

**So do chan (luoi phia tren):**

```
          +------------------------------------------+
          |          RASPBERRY PI PICO               |
          |  [USB]         [SMPS Enable]             |
  VSYS -- |                                        |
  GND  -- |  GP0  GP1  GP2  GP3  GP4  GP5  GP6  GP7   |
  --------+---  ---  ---  ---  ---  ---  ---  ---+    |
  3V3   -- |  GP28 GND  GP27 GP26 GP22 GP21 GP20 GP19  |
  3V3   -- |                                        |
  GND   -- |  GP18 GND  GP17 GP16 RUN  GND  GP15 GP14  |
  --------+---  ---  ---  ---  ----  ---  ---  ---+    |
  ADC0  -- |  GP26(A0) GP22  GP21  ADC_VREF  AGND        |
  ADC1  -- |  GP27(A1) GP20  GP19  GP28(A2)             |
  ADC2  -- |  GP28(A2)                               |
          +------------------------------------------+
```

**GPIO chi tiet cho Pico RP2040:**

| GPIO  | Analog | Chuc nang dac biet          | Su dung trong he thong        |
|-------|--------|----------------------------|------------------------------|
| GP0   | -      | PWM, SPI0 TX               | **Relay CH1 (CO2 Valve)**     |
| GP1   | -      | PWM, SPI0 CSn              | **Relay CH2 (Pump)**         |
| GP2   | -      | PWM, SPI0 SCK              | **Relay CH3 (Fan)**          |
| GP3   | -      | PWM, SPI0 MOSI             | **Relay CH4 (Power Cut)**    |
| GP4   | -      | PWM                        | **Relay CH5 (UPS Switch)**    |
| GP5   | -      | PWM                        | **Relay CH6 (Buzzer)**       |
| GP6   | -      | PWM                        | **Relay CH7 (Light)**        |
| GP7   | -      | PWM                        | **Relay CH8 (Door Lock)**    |
| GP15  | -      | PWM, SPI1 MOSI             | **Buzzer PWM**               |
| GP16  | -      | **I2C0 SDA**              | **I2C giao tiep ESP32**      |
| GP17  | -      | **I2C0 SCL**              | **I2C giao tiep ESP32**      |
| GP18  | -      | PWM, SPI1 SCK             | Optional                     |
| GP19  | -      | PWM, SPI1 MISO            | Optional                     |
| GP20  | -      | PWM, SPI1 MOSI            | Optional                     |
| GP21  | -      | PWM, SPI1 CSn             | Optional                     |
| GP22  | -      | PWM                       | Optional                     |
| GP25  | -      | **Onboard LED**           | Status LED (xanh duong)      |
| GP26  | ADC0   | PWM, I2C1 SDA            | Analog input (3.3V only)     |
| GP27  | ADC1   | PWM, I2C1 SCL            | Analog input (3.3V only)     |
| GP28  | ADC2   | PWM                       | Analog input (3.3V only)     |

---

## Ket noi ESP32 NodeMCU-32S - Cam bien

### So do chan ESP32 NodeMCU-32S (30 pins)

```
        +------------------------------------------+
        |           ESP32 DEVKIT V1                 |
        |                                           |
  3.3V  |--[DHT11]--------[PMS5003]-----[MQ-2]---|
  GND   |--[10K Pull-up]--[GND/5V]------[GND]----|
  GPIO21(SDA)----[I2C]-----[OLED 0.96"]----------|
  GPIO22(SCL)-------------------------------------|
  GPIO32 --[DHT11 Data]-----------[10K Pull-up]--[3.3V]
  GPIO33 --[MQ-2 A0]-----[Voltage Divider 10K]--|
  GPIO34 --[Leak Sensor]--------------------------|
  GPIO35 --[ACS712 A0]---------------------------|
  GPIO26 --[PIR HC-SR501 OUT]--------------------|
  GPIO27 --[Reed Switch]---[10K Pull-up]--[3.3V] |
  GPIO1(TX) --[PMS5003 RX]------------------------|
  GPIO3(RX) --[PMS5003 TX]------------------------|
  GPIO36 --[Voltage Divider - Input Voltage]------|
  GPIO39 --[Voltage Divider - UPS Voltage]--------|
  GPIO2 --[Status LED + 330R]--------------------|
        +------------------------------------------+
```

### So do ket noi chi tiet ESP32 NodeMCU-32S

```
ESP32 NodeMCU-32S CH340 (ESP-WROOM-32, 30 pins)
=================================================================

  VIN/5V ──────────────●──────── 5V nguon (tu USB hoac adapter)
  3V3   ──────────────●──────── 3.3V nguon (max 500mA)
  GND   ──────────────●──────── GND chung

  --- I2C Bus (giao tiep Pico RP2040) ---
  IO21 (SDA) ─────────●──────── Pico GP16 (I2C SDA)
  IO22 (SCL) ─────────●──────── Pico GP17 (I2C SCL)
  (pull-up 4.7K keo len 3.3V)

  --- Cam bien Nhiet Do / Do Am ---
  IO32 ──────────────●──────── DHT11 Data (keo pull-up 10K len 3.3V)

  --- Cam bien Khoi / Gas (Analog) ---
  IO33 ─────────────●──────── MQ-2 A0 (qua voltage divider 10K+10K)

  --- Cam bien Roan Nuoc (Digital, INPUT ONLY) ---
  IO34 ────────────●──────── Leak Sensor D0 (Active LOW, pull-up 10K)

  --- Cam bien Dong Dien (Analog, INPUT ONLY) ---
  IO35 ────────────●──────── ACS712 OUT (qua voltage divider)

  --- Cam bien Chuyen Dong ---
  IO26 ──────────────●──────── PIR HC-SR501 OUT (5V tolerant)

  --- Cam bien Cua ---
  IO27 ──────────────●──────── Reed Switch (pull-up 10K len 3.3V)

  --- Cam bien Dien Ap AC (INPUT ONLY) ---
  IO36 ────────────●──────── Voltage Divider cho AC Input (100K+10K)

  --- Cam bien Dien Ap UPS (INPUT ONLY) ---
  IO39 ────────────●──────── Voltage Divider cho UPS Output (20K+10K)

  --- Dust Sensor PMS5003 (UART2) ---
  IO17 (TX2) ───────●──────── PMS5003 RX
  IO16 (RX2) ───────●──────── PMS5003 TX

  --- Onboard LED ---
  IO2 ──────────────●──────── Onboard LED (co san, sang khi LOW)

=================================================================
```

### Cam bien chi tiet ESP32 NodeMCU-32S

| STT | Cam bien | Model | Chan ESP32 | Loai | Nguon | Loi noi |
|-----|----------|-------|------------|------|-------|---------|
| 1 | Nhiet do/Do am | **DHT11** | IO32 | Digital | 3.3V | IO32 -> Data, 10K pull-up -> 3.3V |
| 2 | Bu PM2.5 | PMS5003 | GPIO1(TX), GPIO3(RX) | UART | 5V | Baud 9600, 8N1 |
| 3 | Khoi/Gas | MQ-2 | GPIO33 | Analog | 5V | Qua voltage divider 10K |
| 4 | Ro nuoc | Leak Sensor | GPIO34 | Digital (Active LOW) | 3.3V | Active LOW khi co nuoc |
| 5 | Ro dien | ACS712 (30A) | GPIO35 | Analog | 5V | Output 1.65V @ 0A |
| 6 | Chuyen dong | HC-SR501 | GPIO26 | Digital | 5V | Co jumper: H/L |
| 7 | Cua mo | Reed Switch | GPIO27 | Digital (Pull-up) | 3.3V | NAM = dong, NPN = mo |
| 8 | Dien ap | Voltage Divider | GPIO36, GPIO39 | Analog | 5V | R1=100K, R2=10K |
| 9 | (chi ro le) | - | - | - | - | IO34=Leak, IO35=Current |
| 10 | (chi ro le) | - | - | - | - | IO36=AC Volts, IO39=UPS Volts |

**Luu y quan trong ve ESP32 NodeMCU-32S:**
- **IO34, IO35, IO36, IO39**: Chi INPUT ONLY, khong co pull-up/pull-down noi, khong dung cho output/PWM
- **IO32, IO33**: Co pull-down noi san, co the dung cho analog/digital input
- **UART2 (IO16/IO17)**: Dung cho PMS5003 thay vi UART0 (GPIO1/GPIO3) de giu UART0 cho debug/flash
- **I2C (IO21/IO22)**: Dung giao tiep I2C voi Pico RP2040

### Dien tro ke (Voltage Divider) cho MQ-2 va ACS712

```
MQ-2 / ACS712 Output
        |
       [10K]
        |
        +------- GPIO33/GPIO35 (ESP32 ADC)
        |
       [10K]
        |
       GND
```

### Voltage Divider cho do dien ap (220V -> <3.3V)

```
220V AC (qua bien ap cach ly)
        |
       [100K]
        |
        +------- GPIO36 (ESP32 ADC)
        |
       [10K]
        |
       GND
```

---

## Ket noi Pico RP2040 - Relay

### So do chan Pico RP2040 (40 pins)

```
        +------------------------------------------+
        |         RASPBERRY PI PICO                  |
        |                                           |
  VSYS --[5V Power Adapter 2A+]--------------------|
  GND  --[GND chung]-------------------------------|
  GP0  --[Relay CH1 - CO2 Solenoid Valve]----------|
  GP1  --[Relay CH2 - Water Pump]------------------|
  GP2  --[Relay CH3 - Exhaust Fan]----------------|
  GP3  --[Relay CH4 - Main Power Cutoff]----------|
  GP4  --[Relay CH5 - UPS Switch]-----------------|
  GP5  --[Relay CH6 - Buzzer/Alarm]----------------|
  GP6  --[Relay CH7 - Warning Light]---------------|
  GP7  --[Relay CH8 - Door Lock]-------------------|
  GP16(I2C SDA) <---> ESP32 GPIO21 (I2C)---------|
  GP17(I2C SCL) <---> ESP32 GPIO22 (I2C)---------|
  GP15 --[Buzzer PWM]----------------------------|
  GP25 --[Status LED]----------------------------|
  GP26 --[Optional: Button]-----------------------|
        +------------------------------------------+
```

### Relay 8-Channel - Chi tiet noi day

```
Pico RP2040          Relay Module (8-kan)         Thiet bi ngoai
-----------          --------------------         --------------
GP0  (Signal) ------> IN1 -----------------------> Chua noi
GP1  (Signal) ------> IN2 -----------------------> Chua noi
GP2  (Signal) ------> IN3 -----------------------> Chua noi
GP3  (Signal) ------> IN4 -----------------------> Chua noi
GP4  (Signal) ------> IN5 -----------------------> Chua noi
GP5  (Signal) ------> IN6 -----------------------> Chua noi
GP6  (Signal) ------> IN7 -----------------------> Chua noi
GP7  (Signal) ------> IN8 -----------------------> Chua noi

5V (Nguon rieng!) --> VCC -----------------------> [QUAN TRONG: Nguon 5V/2A rieng]

GND (Chung) ------> GND -----------------------> GND chung

Relay Module              Thiet bi ngoai
JD-VCC (Jumper) ----> [Remove jumper] ----> Nguon 5V/10A rieng
                                           |
COM (Moi kenh) -----> Nguon thiet bi (220V/12V)
NO  (Moi kenh) -----> Thiet bi (thong thuong dong)
NC  (Moi kenh) -----> Thiet bi (thong thuong ngat)
```

### Bang kenh Relay

| Kenh | Chan Pico | Ten thiet bi | Loai tai | Cong suat |
|------|-----------|--------------|----------|-----------|
| CH1 | GP0 | CO2 Solenoid Valve | Inductive | 24V AC |
| CH2 | GP1 | Water Pump | Inductive | 220V/100W |
| CH3 | GP2 | Exhaust Fan | Motor | 220V/50W |
| CH4 | GP3 | Main Power Cutoff | Resistive | Contactor |
| CH5 | GP4 | UPS Switch | Signal | 12V |
| CH6 | GP5 | Buzzer/Alarm | Buzzer | 12V/500mA |
| CH7 | GP6 | Warning Light | Lamp | 220V/25W |
| CH8 | GP7 | Door Lock | Solenoid | 12V/1A |

---

## So do nguon

```
AC 220V
   |
   +---> [Circuit Breaker 20A] -----> [Server Rack PDU]
   |                                    |
   +---> [UPS 12V/7Ah] -----------------+
   |        |                            |
   |        +---> ESP32 (USB 5V/1A)
   |        +---> Pico RP2040 (VSYS 5V/1A)
   |        +---> WiFi Router (12V/1A)
   |        +---> Camera (12V/1A)
   |        +---> Warning Light (12V)
   |
   +---> [5V/10A Adapter] ---> Relay Module VCC
   |
   +---> [24V Adapter] ---> Solenoid Valves
```

### Luat an toan nguon:

- Relay Module BAT BUOC co nguon rieng 5V/10A (KHONG lay tu Pico)
- Pico chi truyen tin hieu (GPIO -> Relay IN)
- Tat ca GND phai noi chung (ESP32, Pico, Relay GND)
- ESP32 VIN co the nhan 5V-12V, co onboard 3.3V regulator
- Pico VSYS recommend 5V, co onboard regulator
- Dung 220V can co Circuit Breaker va GFCI/RCD

---

## Ket noi UPS

### Cam bien dien ap UPS

```
220V AC (qua bien ap cach ly 10:1)
        |
       [100K, 2W]
        |
        +---> IO36 INPUT ONLY (ESP32 ADC)
        |
       [10K, 0.5W]
        |
       GND
```

### Cam bien dien ap dau ra UPS

```
12V UPS Output
        |
       [20K]
        |
        +---> IO39 INPUT ONLY (ESP32 ADC)
        |
       [10K]
        |
       GND
```

**Luu y:**
- IO36 va IO39 chi la INPUT ONLY, khong co pull-up/pull-down
- Dung voltage divider de ha ap xuong muc an toan cho ESP32 ADC (max 3.3V)

---

## Ket noi Camera AI

### ESP32-CAM (AI Thinker)

```
ESP32-CAM
   |
   +--->UILT-IN CAMERA MODULE
   |
   +---> GPIO4 ---> Status LED (co san)
   +---> GPIO33 ---> Optional external flash
   |
   +---> USB (for programming) ---> USB-TTL Adapter
   |    (GPIO0 -> GND de vao che do flash)
   |
   +---> WiFi ---> MQTT Broker ---> Backend AI
```

### Ket noi USB-TTL de nap code

```
ESP32-CAM          USB-TTL Adapter
---------          ----------------
U0R (RX)    <----> TX
U0T (TX)    ----> RX
GND         <----> GND
5V          <----> (TUY CHON - neu USB nhu du 500mA)
           ----> 5V External (neu can 2A)
GPIO0       <----> GND (khi nap code, nhan giu nut boot)

LUU Y: Khi nap xong, nha GPIO0 khoi GND va nhan RESET
```

---

## Bang noi day chi tiet

### ESP32 NodeMCU-32S CH340

| STT | Cam bien | Model | VCC | Signal | Chan ESP32 | Ghi chu |
|-----|----------|-------|-----|--------|-----------|---------|
| 1 | Nhiet do/Do am | **DHT11** | 3.3V | Data | IO32 | 10K pull-up |
| 2 | Bu PM2.5 | PMS5003 | 5V | TX/RX | TX2=IO17, RX2=IO16 | UART2, Baud 9600 |
| 3 | Khoi/Gas | MQ-2 | 5V | A0 | IO33 | Voltage divider 10K |
| 4 | Roan Nuoc | Leak Sensor | 3.3V | D0 | IO34 | INPUT ONLY, Active LOW |
| 5 | Roan Dien | ACS712 30A | 5V | A0 | IO35 | INPUT ONLY, 1.65V @ 0A |
| 6 | Chuyen Dong | HC-SR501 | 5V | OUT | IO26 | Jumper H |
| 7 | Cua Mo | Reed Switch | 3.3V | OUT | IO27 | Pull-up 10K |
| 8 | Dien ap V_in | Divider | - | A0 | IO36 | INPUT ONLY, 100K/10K |
| 9 | Dien ap UPS | Divider | - | A0 | IO39 | INPUT ONLY, 20K/10K |
| 10 | I2C (Pico) | - | 3.3V | SDA/SCL | SDA=IO21, SCL=IO22 | Pull-up 4.7K |

### Pico RP2040

| STT | Thiet bi | Signal | Chan Pico | Nguon | Ghi chu |
|-----|----------|--------|-----------|-------|---------|
| 1 | Relay CH1 (CO2) | Signal | GP0 | 5V rieng | Normally Open |
| 2 | Relay CH2 (Pump) | Signal | GP1 | 5V rieng | Normally Open |
| 3 | Relay CH3 (Fan) | Signal | GP2 | 5V rieng | Normally Open |
| 4 | Relay CH4 (Power Cut) | Signal | GP3 | 5V rieng | Normally Open |
| 5 | Relay CH5 (UPS) | Signal | GP4 | 5V rieng | Normally Open |
| 6 | Relay CH6 (Buzzer) | Signal | GP5 | 5V rieng | PWM capable |
| 7 | Relay CH7 (Light) | Signal | GP6 | 5V rieng | Normally Open |
| 8 | Relay CH8 (Lock) | Signal | GP7 | 5V rieng | Normally Open |
| 9 | ESP32 I2C | SDA | GP16 | 3.3V | Pull-up 4.7K |
| 10 | ESP32 I2C | SCL | GP17 | 3.3V | Pull-up 4.7K |
| 11 | Buzzer | PWM | GP15 | - | PWM signal |
| 12 | Onboard LED | - | GP25 | - | Xanh duong, co san |

---

## Cac buoc kiem tra

### 1. Kiem tra ESP32 NodeMCU-32S CH340

```bash
# 1. Nap code ESP32 (Arduino IDE)
# Board: "ESP32 Dev Module"
# Upload Speed: 115200
# Flash Frequency: 80MHz
# Partition Scheme: Default (2MB APP / 2MB SPIFFS)

# 2. Kiem tra Serial Monitor (115200 baud)
# Nen thay: "WiFi connected", "MQTT connected"
# Neu khong ket noi WiFi, se tao AP "AI-Guardian-Setup" (password: 12345678)

# 3. Kiem tra CH340 driver (Windows)
# Neu khong nhan duoc COM port, tai driver tai:
# https://www.wch-ic.com/downloads/CH341SER_ZIP.html
```

### 2. Kiem tra Pico RP2040

```python
# 1. Nap code bang Thonny Python (khuyen nghi)
# - Cai dat Thonny: https://thonny.org/
# - Chon Python (Raspberry Pi Pico)
# - Copy main.py vao Pico

# 2. Hoac nap code bang pico-tool:
# - Gian giut BOOTSEL + cam USB
# - Copy main.py vao drive "RPI-RP2"

# 3. Kiem tra Serial Monitor (115200 baud)
# Nen thay: "MQTT connected"

# 4. Test relay thu cong:
from machine import Pin
relay = Pin(0, Pin.OUT)
relay.value(1)  # Bat relay (LED relay sang)
relay.value(0)  # Tat relay

# 5. Kiem tra onboard LED (GP25):
led = Pin(25, Pin.OUT)
led.value(1)  # Sang
led.value(0)  # Tat
```

### 3. Kiem tra I2C giua ESP32 va Pico

```python
# Tren Pico:
from machine import I2C, Pin
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
print("I2C devices:", i2c.scan())  # Nen thay [32] neu ESP32 co I2C slave

# Tren ESP32 (Arduino):
# Su dung Wire.h (I2C master)
# I2C address thuong la 0x20 hoac 0x21
```

### 4. Kiem tra toan he thong

```bash
# 1. Khoi dong Docker services
cd data
docker-compose up -d

# 2. Kiem tra logs
docker-compose logs -f

# 3. Khoi dong backend
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

# 4. Truy cap dashboard
# http://localhost:8000/dashboard
```

---

## Luat an toan

### CANH BAO NGHIEM TRONG VE DIEN

1. **TUYET DOI KHONG** noi truc tiep ESP32/Pico vao 220V
2. **LUON** su dung Relay de cach ly dien cao ap
3. **BAT BUOC** co Circuit Breaker 20A cho mach 220V
4. **BAT BUOC** co GFCI/RCD phat hien ro dien
5. **DUNG** day dien 220V co tiet dien du (toi thieu 1.5mm2)
6. Tat ca day 220V phai co vo cach dien

### ESP32-CAM

1. Can nguon 5V/2A rieng (khong dung chung USB)
2. Lap tan nhiet cho ESP32-CAM (nhiet do hoat dong cao)
3. Tranh de camera trong moi truong nhiet do cao

### MQTT Security

1. Doi mat khau mac dinh truoc khi trien khai production
2. Su dung TLS (port 8883) cho production
3. Khong dung allow_anonymous: true trong production
