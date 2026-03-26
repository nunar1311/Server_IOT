# AI-Guardian - API Documentation

Base URL: `http://localhost:8000`

---

## Sensors API

### Receive Sensor Data

```
POST /api/sensors
Content-Type: application/json
```

**Request Body:**

```json
{
    "node": "esp32_sensor_node",
    "temperature": 32.5,
    "humidity": 65.2,
    "dust_pm25": 12.3,
    "dust_pm10": 18.7,
    "gas": 15.0,
    "motion": false,
    "door": false,
    "leak": false,
    "current_leak": 0.5,
    "voltage_input": 220.0,
    "voltage_ups": 12.3,
    "rssi": -65,
    "uptime": 86400
}
```

**Response:**

```json
{
    "status": "ok",
    "id": "65abc123...",
    "anomaly": {
        "is_anomaly": true,
        "score": 0.75,
        "contributing_features": {"temperature": 32.5}
    },
    "fire_analysis": {
        "is_fire": false,
        "risk_score": 0.1,
        "details": {}
    },
    "component_health": {
        "temperature_sensor": 85.0,
        "humidity_sensor": 80.0
    }
}
```

### Get Latest Sensor Data

```
GET /api/sensors/latest?node=esp32_sensor_node
```

**Response:** `SensorDataResponse` object or `null`

### Get Sensor History

```
GET /api/sensors/history?node=esp32_sensor_node&hours=24&limit=100
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| node | string | esp32_sensor_node | Sensor node ID |
| hours | int | 24 | Hours of history (max 168) |
| limit | int | 100 | Max records (max 1000) |

**Response:**

```json
{
    "count": 50,
    "data": [SensorDataResponse, ...]
}
```

### Get Sensor Statistics

```
GET /api/sensors/stats?node=esp32_sensor_node&hours=24
```

**Response:**

```json
{
    "node": "esp32_sensor_node",
    "period": "24h",
    "avg_temperature": 28.5,
    "avg_humidity": 62.0,
    "avg_dust_pm25": 15.2,
    "avg_gas": 12.0,
    "max_temperature": 35.0,
    "max_gas": 25.0,
    "max_dust_pm25": 22.0,
    "total_motion_events": 8,
    "total_leak_events": 0,
    "total_door_events": 5,
    "record_count": 288
}
```

---

## Alerts API

### Get Alerts

```
GET /api/alerts?limit=50&acknowledged=false&severity=warning&node=esp32_sensor_node
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | int | Max alerts to return (default 50) |
| acknowledged | bool | Filter by acknowledged status |
| severity | string | Filter by severity: info, warning, critical, emergency |
| node | string | Filter by node ID |

**Response:**

```json
{
    "total": 125,
    "alerts": [
        {
            "id": "65abc123...",
            "type": "temperature_high",
            "severity": "warning",
            "message": "WARNING: Temperature 48C exceeds 45C",
            "node": "esp32_sensor_node",
            "sensor_reading": {...},
            "triggered_value": 48.0,
            "threshold_value": 45.0,
            "acknowledged": false,
            "acknowledged_by": null,
            "acknowledged_at": null,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### Acknowledge Alert

```
POST /api/alerts/{alert_id}/acknowledge
Content-Type: application/json
```

**Request Body:**

```json
{
    "acknowledged_by": "admin"
}
```

### Clear Acknowledged Alerts

```
DELETE /api/alerts
```

**Response:**

```json
{
    "deleted": 10
}
```

---

## Incidents API

### Create Incident

```
POST /api/incidents
Content-Type: application/json
```

**Request Body:**

```json
{
    "title": "Fire alarm triggered",
    "description": "Temperature exceeded 55C threshold",
    "severity": "critical",
    "source": "system",
    "sensor_reading": {...}
}
```

**Response:** `IncidentResponse` object

### Get Incidents

```
GET /api/incidents?limit=50&status=open
```

### Update Incident

```
PATCH /api/incidents/{incident_id}
Content-Type: application/json
```

**Request Body:**

```json
{
    "status": "resolved",
    "notes": "Temperature normalized after 10 minutes",
    "resolved_by": "admin"
}
```

---

## Actions API

### Trigger Action

```
POST /api/actions
Content-Type: application/json
```

**Request Body:**

```json
{
    "action": "fire",
    "priority": "critical",
    "devices": null
}
```

**Actions:**

| Action | Description | Priority |
|--------|-------------|----------|
| fire | Fire emergency - buzzer, light, CO2, fan, cut power | critical |
| flood | Flood response - pump, buzzer, light, cut power | critical |
| gas_leak | Gas leak - fan, buzzer, light, cut power | critical |
| electric_leak | Electric leak - buzzer, light, cut power immediately | critical |
| intrusion | Intrusion - buzzer, light, lock door | high |
| temp_high | High temperature - fan only | normal |
| clear | Clear all actuators | normal |
| reset | Reset all actuators | normal |
| manual | Manual control - specify devices below | normal |

**Manual Control Example:**

```json
{
    "action": "manual",
    "priority": "normal",
    "devices": {
        "buzzer": true,
        "warning_light": true,
        "fan": false
    }
}
```

---

## AI API

### Get Component Health

```
GET /api/ai/health?node=esp32_sensor_node
```

**Response:**

```json
{
    "temperature_sensor": 85.0,
    "humidity_sensor": 80.0,
    "gas_sensor": 95.0,
    "dust_sensor": 90.0,
    "electrical_system": 92.0,
    "overall": 88.5
}
```

### Get AI Predictions

```
GET /api/ai/predictions?node=esp32_sensor_node
```

**Response:**

```json
{
    "temperature_failure": {
        "type": "temperature_critical",
        "predicted_value": 58.5,
        "threshold": 55,
        "hours_until_failure": 2.5,
        "confidence": "medium",
        "trend": "rising"
    },
    "gas_leak_trend": null,
    "maintenance_alerts": [
        {
            "type": "maintenance",
            "priority": "medium",
            "message": "Temperature trending upward. Check cooling system."
        }
    ],
    "component_health": {...}
}
```

---

## WebSocket

### Endpoint

```
ws://localhost:8000/ws/live
```

### Messages from Server

**Sensor Update:**

```json
{
    "type": "sensor_update",
    "data": {
        "temperature": 32.5,
        "humidity": 65.2,
        "dust_pm25": 12.3,
        "gas": 15.0,
        "motion": false,
        "door": false,
        "leak": false,
        "current_leak": 0.5,
        "voltage_ups": 12.3,
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

**Alert:**

```json
{
    "type": "alert",
    "data": {
        "type": "temperature_high",
        "severity": "warning",
        "message": "Temperature 48C exceeds 45C",
        "node": "esp32_sensor_node",
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

### Messages to Server

```json
"ping"
```

---

## Dashboard

```
GET /dashboard
```

Returns an HTML page with embedded JavaScript for real-time monitoring.

---

## Health Check

```
GET /health
```

**Response:**

```json
{
    "status": "healthy",
    "mongodb": "connected",
    "mqtt": "connected",
    "timestamp": "2024-01-15T10:30:00Z"
}
```
