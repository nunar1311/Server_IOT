# AI-Guardian

Hệ thống giám sát & phản ứng sự cố phòng server thông minh ứng dụng IoT và AI.

## Tính năng

- Giám sát nhiệt độ, độ ẩm, bụi PM2.5, khí gas, rò nước, rò điện
- Phát hiện chuyển động, trạng thái cửa, điện áp UPS
- **Màn hình OLED 1.3" SH1106** hiển thị dữ liệu realtime (I2C)
- Phản ứng tự động: cắt điện, bật báo động, CO2, quạt, bơm
- AI phát hiện bất thường, dự đoán hỏng hóc
- ESP32-CAM cho nhận diện cháy, khuôn mặt, phát hiện ngã
- Dashboard web realtime

## Cấu trúc thư mục

```
Server_IOT/
├── hardware/           # Code cho ESP32, Pico RP2040, ESP32-CAM
├── backend/            # FastAPI + AI modules
├── dashboard/           # Web dashboard
├── data/                # Docker config (MongoDB, Mosquitto)
└── docs/                # Tài liệu
```

## Triển khai

### 1. Infrastructure (Docker)

```bash
cd data
docker-compose up -d
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

### 3. Dashboard

```bash
cd dashboard
python app.py
```

### 4. Hardware

Xem chi tiết trong `docs/wiring_diagram.md`

## Kiến trúc

- **ESP32**: Thu thập dữ liệu cảm biến, gửi qua MQTT, hiển thị OLED
- **Pico RP2040**: Nhận lệnh từ MQTT, điều khiển relay/actuator
- **ESP32-CAM**: AI xử lý hình ảnh
- **MQTT Broker**: Mosquitto
- **Database**: MongoDB
- **Backend**: FastAPI + TensorFlow/PyTorch AI
- **Dashboard**: Flask + Chart.js

## Màn hình OLED (Tùy chọn)

ESP32 có thể gắn thêm **màn hình OLED 1.3" SH1106** qua I2C để hiển thị dữ liệu cảm biến realtime mà không cần dashboard.

**Sơ đồ đấu dây:**

```
ESP32 NodeMCU-32S    OLED 1.3" SH1106
==================   =================
3.3V          ────>  VCC
GND           ────>  GND
IO21 (SDA)    ────>  SDA
IO22 (SCL)    ────>  SCL
```

**Thư viện cần cài đặt:**
- `Adafruit GFX Library`
- `Adafruit SH110X`

**Nội dung hiển thị:**
- Nhiệt độ, độ ẩm, PM2.5
- Gas, dòng rò, điện áp AC/UPS
- Trạng thái cảnh báo (chuyển động, rò nước, cửa mở)
- RSSI WiFi, uptime

**Cài đặt địa chỉ I2C:**
- Mặc định: `0x3C`
- Nếu màn hình trắng: đổi sang `0x3D`

**Cập nhật tự động:** mỗi 3 giây

Xem chi tiết trong `hardware/esp32_sensor_node/oled.h`.
