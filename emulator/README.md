# AI-Guardian - Pico RP2040 Emulator for Windows

## Tom tat

Pico RP2040 Emulator la phan mem giai lap Raspberry Pi Pico RP2040 tren Windows, cho phep thay the hardware thuc ma van nhan duoc cac MQTT commands tu he thong AI-Guardian.

**Thay vi can:**
- Raspberry Pi Pico RP2040
- Day noi USB
- Relay module 8 kenh
- Nguon 5V

**Ban chi can:**
- Windows 10/11
- Python 3.8+
- MQTT broker (Mosquitto)

---

## Tinh nang

- **8 relay ao** (GP0-GP7): CO2, Pump, Fan, Power Cut, UPS, Buzzer, Light, Door
- **MQTT integration**: Subscribe topic `ai-guardian/actions`, publish status/ack
- **Console UI**: Mau sac ANSI, box drawing characters
- **GUI mode**: Tkinter, bam nut de dieu khien
- **Buzzer sounds**: winsound (Windows native)
- **Actions tu dong**: fire, flood, gas_leak, electric_leak, intrusion, temp_high, clear, reset, manual
- **Build EXE**: Chay nhu ung dung Windows binh thuong

---

## Cau truc thu muc

```
emulator/
├── pico_emulator/
│   ├── __init__.py          # Package init
│   ├── __main__.py         # Entry point (python -m)
│   ├── main.py             # Main entry point
│   ├── config.py           # Cau hinh MQTT, relay map
│   ├── emulator_core.py    # Core logic relay + action handlers
│   ├── mqtt_client.py      # MQTT client (paho-mqtt)
│   ├── sound_manager.py     # Buzzer sound (winsound)
│   ├── ui_console.py       # Console UI (ANSI colors)
│   └── ui_tkinter.py        # Tkinter GUI
├── requirements.txt         # Dependencies
├── build.bat                # Build EXE (console mode)
├── build_gui.bat           # Build EXE (GUI mode)
└── README.md               # File nay
```

---

## Cai dat

### 1. Cai dat Python

Kiem tra Python da cai dat chua:

```bash
python --version
```

Neu chua co, tai tai: https://www.python.org/downloads/

### 2. Cai dat dependencies

```bash
cd emulator
python -m pip install -r requirements.txt
```

Hoac:

```bash
pip install paho-mqtt pyinstaller
```

---

## Su dung

### Cach 1: Chay nhu Python script

#### Console Mode (mac dinh)

```bash
cd emulator
python -m pico_emulator --console
```

Hoac:

```bash
cd emulator/pico_emulator
python main.py
```

#### GUI Mode

```bash
cd emulator
python -m pico_emulator --gui
```

#### Tat am thanh

```bash
python -m pico_emulator --console --no-sound
```

#### Custom MQTT broker

```bash
python -m pico_emulator --broker 192.168.1.100 --port 1883
```

### Cach 2: Build thanh EXE

#### Build Console EXE

```bash
cd emulator
.\build.bat
```

File EXE se o: `dist\PicoEmulator.exe`

#### Build GUI EXE

```bash
cd emulator
.\build_gui.bat
```

File EXE se o: `dist\PicoEmulatorGUI.exe`

---

## Console Commands

Khi chay o console mode, ban co the nhap cac lenh sau:

| Lenh | Mo ta |
|------|-------|
| `fire` | Kich hoat bao chay (buzzer, light, co2, fan, power) |
| `flood` | Kich hoat phong nguap (buzzer, pump, light, power) |
| `gas_leak` | Kich hoat bao ro ri gas (buzzer, fan, light, power) |
| `electric_leak` | Kich hoat bao ro dien (buzzer, light, power) |
| `intrusion` | Kich hoat bao xam nhap (buzzer, light, door_lock) |
| `temp_high` | Nhiet do cao (fan, [buzzer+light neu critical]) |
| `clear` | Tat ca OFF, beep OK |
| `reset` | Tat ca OFF |
| `manual <device> <on\|off>` | Dieu khien thu cong vi du: `manual buzzer on` |
| `status` | Hien thi trang thai hien tai |
| `sound on` | Bat am thanh |
| `sound off` | Tat am thanh |
| `exit`, `quit`, `q` | Thoat |

---

## MQTT Topics

Emulator hoat dong giong nhu Pico RP2040 thuc, su dung cac MQTT topics:

| Topic | Direction | Payload |
|-------|----------|---------|
| `ai-guardian/actions` | **Subscribe** | `{"action": "fire", "priority": "critical"}` |
| `ai-guardian/actuator/status` | Publish (30s) | `{"node": "pico_emulator_win", "state": {...}}` |
| `ai-guardian/actuator/ack` | Publish | `{"node": "pico_emulator_win", "action": "fire", "status": "handled"}` |

### MQTT Credentials

| Setting | Gia tri mac dinh |
|---------|------------------|
| Broker | `localhost` (hoac IP cua server) |
| Port | `1883` |
| Username | `mqtt_user` |
| Password | `mqtt_password` |

---

## Relay Mapping

| GP Pin | Ten | Mo ta | Thiet bi |
|--------|-----|-------|----------|
| GP0 | co2 | Van CO2 | Solenoid Valve |
| GP1 | pump | May bom | Water Pump |
| GP2 | fan | Quat hut | Exhaust Fan |
| GP3 | power_cut | Cat nguon | Main Power Cutoff |
| GP4 | ups_switch | Chuyen UPS | UPS Switch |
| GP5 | buzzer | Coi bao | Buzzer/Alarm |
| GP6 | warning_light | Den canh bao | Warning Light |
| GP7 | door_lock | Khoa cua | Door Lock |

---

## Action Response

| Action | Buzzer | Light | CO2 | Pump | Fan | Power | Lock |
|--------|--------|-------|-----|------|-----|-------|------|
| `fire` | ON | ON | ON | - | ON | ON* | - |
| `flood` | ON | ON | - | ON | - | ON* | - |
| `gas_leak` | ON | ON | - | - | ON | ON* | - |
| `electric_leak` | ON | ON | - | - | - | ON | - |
| `intrusion` | ON | ON | - | - | - | - | ON |
| `temp_high` | ON** | ON** | - | - | ON | - | - |
| `clear` | OFF | OFF | OFF | OFF | OFF | OFF | OFF |
| `reset` | OFF | OFF | OFF | OFF | OFF | OFF | OFF |

`*` Chi khi `priority: critical`
`**` Chi khi `priority: critical`

---

##拚 (Buzzer Patterns)

| Pattern | Mo ta | Tan so |
|---------|-------|--------|
| `emergency` | 5x beep nhanh | 2000Hz |
| `warning` | 3x beep vua | 1500Hz |
| `ok` | 1x beep ngan | 1000Hz |

---

## Khac phuc su co

### Loi: "pip not recognized"

Su dung:

```bash
python -m pip install paho-mqtt
```

### Loi: "No connection could be made"

Dich vu MQTT chua chay. Khoi dong Docker:

```bash
cd data
docker-compose up -d
```

Kiem tra Mosquitto:

```bash
docker-compose ps
```

### Loi: "Module not found"

Dam bao da chay tu thu muc `emulator`:

```bash
cd emulator
python -m pico_emulator
```

### Loi: Console UI khong hien thi mau sac

Su dung Windows Terminal hoac PowerShell 7+. Hoac chay GUI mode thay the:

```bash
python -m pico_emulator --gui
```

---

## Viet them module

Neu ban muon mo rong emulator, them code vao:

- `emulator_core.py`: Logic xu ly relay va actions
- `mqtt_client.py`: Xu ly MQTT connection
- `sound_manager.py`: Them am thanh moi
- `ui_console.py`: Thay doi giao dien console
- `ui_tkinter.py`: Thay doi giao dien GUI

---

## Lien he va ho tro

- Repository: AI-Guardian Project
- MQTT Broker: Mosquitto (docker-compose)
- Backend: FastAPI + MongoDB

---

## Ban quyen

AI-Guardian Project - 2026
