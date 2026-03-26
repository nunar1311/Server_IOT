# ============================================================
# AI-Guardian - FastAPI Main Application
# Backend server with REST API and WebSocket support
# ============================================================

import asyncio
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from bson import ObjectId

from database import get_database, close_connections
from models.sensor_data import SensorData, SensorDataCreate, SensorDataResponse, SensorStats
from models.alerts import AlertCreate, AlertResponse, AlertAcknowledge, AlertListResponse
from models.incidents import IncidentCreate, IncidentResponse, IncidentUpdate, IncidentListResponse
from mqtt_listener import get_mqtt_listener
from ai.anomaly_detection import detect_anomaly, get_anomaly_detector
from ai.predictive_maintenance import get_predictor
from ai.fire_detection import get_fire_detector


# ===================== LIFESPAN =====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("AI-Guardian Backend starting...")
    mqtt_thread = threading.Thread(target=get_mqtt_listener().start, daemon=True)
    mqtt_thread.start()
    print("MQTT listener started in background thread")
    yield
    # Shutdown
    print("AI-Guardian Backend shutting down...")
    get_mqtt_listener().stop()
    await close_connections()


# ===================== APP =====================
app = FastAPI(
    title="AI-Guardian API",
    description="Smart server room monitoring & incident response system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===================== WEBSOCKET MANAGER =====================
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        for conn in disconnected:
            self.active_connections.remove(conn)


manager = ConnectionManager()


# ===================== HELPER =====================
def serialize_doc(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc


# ===================== ROOT =====================
@app.get("/", tags=["System"])
async def root():
    return {
        "name": "AI-Guardian Backend",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "sensors": "/api/sensors",
            "alerts": "/api/alerts",
            "incidents": "/api/incidents",
            "dashboard": "/dashboard",
            "websocket": "/ws/live"
        }
    }


# ===================== SENSOR API =====================
@app.post("/api/sensors", response_model=dict, tags=["Sensors"])
async def receive_sensor_data(data: SensorDataCreate):
    """Receive and store sensor data from ESP32 node."""
    db = get_database()

    sensor_dict = data.model_dump()
    if isinstance(sensor_dict.get("timestamp"), datetime):
        sensor_dict["timestamp"] = sensor_dict["timestamp"]
    else:
        sensor_dict["timestamp"] = datetime.utcnow()
    sensor_dict["received_at"] = datetime.utcnow()

    result = db.sensor_logs.insert_one(sensor_dict)
    sensor_dict["_id"] = result.inserted_id

    anomaly = detect_anomaly(sensor_dict)
    fire_result = get_fire_detector().evaluate(sensor_dict)
    predictor = get_predictor()
    predictor.add_reading(sensor_dict)
    health = predictor.calculate_component_health(sensor_dict)

    alerts_to_create = []
    if anomaly:
        alerts_to_create.append({
            "type": "anomaly_detected",
            "severity": "warning",
            "message": f"AI anomaly detected (score: {anomaly['score']:.3f})",
            "node": data.node,
            "sensor_reading": sensor_dict,
            "ai_analysis": anomaly,
            "created_at": datetime.utcnow()
        })

    if fire_result and fire_result.get("is_fire"):
        severity = "emergency" if fire_result["risk_score"] >= 0.8 else "critical"
        alerts_to_create.append({
            "type": "fire_risk",
            "severity": severity,
            "message": f"Fire risk detected (score: {fire_result['risk_score']:.3f})",
            "node": data.node,
            "sensor_reading": sensor_dict,
            "ai_analysis": fire_result,
            "created_at": datetime.utcnow()
        })

    if alerts_to_create:
        db.alerts.insert_many(alerts_to_create)
        for alert in alerts_to_create:
            await manager.broadcast({"type": "alert", "data": alert})

    response = {
        "status": "ok",
        "id": str(result.inserted_id),
        "anomaly": anomaly,
        "fire_analysis": fire_result,
        "component_health": health
    }

    await manager.broadcast({
        "type": "sensor_update",
        "data": {
            "temperature": data.temperature,
            "humidity": data.humidity,
            "dust_pm25": data.dust_pm25,
            "gas": data.gas,
            "motion": data.motion,
            "door": data.door,
            "leak": data.leak,
            "current_leak": data.current_leak,
            "voltage_ups": data.voltage_ups,
            "timestamp": datetime.utcnow().isoformat()
        }
    })

    return response


@app.get("/api/sensors/latest", response_model=Optional[SensorDataResponse], tags=["Sensors"])
async def get_latest_sensor_data(node: str = "esp32_sensor_node"):
    """Get the most recent sensor reading."""
    db = get_database()
    doc = db.sensor_logs.find_one({"node": node}, sort=[("timestamp", -1)])
    if not doc:
        return None
    return serialize_doc(doc)


@app.get("/api/sensors/history", tags=["Sensors"])
async def get_sensor_history(
    node: str = "esp32_sensor_node",
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=100, ge=1, le=1000)
):
    """Get historical sensor data."""
    db = get_database()
    since = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.sensor_logs.find({
        "node": node,
        "timestamp": {"$gte": since}
    }).sort("timestamp", -1).limit(limit)
    results = [serialize_doc(doc) for doc in cursor]
    return {"count": len(results), "data": results}


@app.get("/api/sensors/stats", response_model=SensorStats, tags=["Sensors"])
async def get_sensor_stats(
    node: str = "esp32_sensor_node",
    hours: int = Query(default=24, ge=1, le=720)
):
    """Get aggregated sensor statistics."""
    db = get_database()
    since = datetime.utcnow() - timedelta(hours=hours)

    pipeline = [
        {"$match": {"node": node, "timestamp": {"$gte": since}}},
        {"$group": {
            "_id": "$node",
            "avg_temperature": {"$avg": "$temperature"},
            "avg_humidity": {"$avg": "$humidity"},
            "avg_dust_pm25": {"$avg": "$dust_pm25"},
            "avg_gas": {"$avg": "$gas"},
            "max_temperature": {"$max": "$temperature"},
            "max_gas": {"$max": "$gas"},
            "max_dust_pm25": {"$max": "$dust_pm25"},
            "total_motion_events": {"$sum": {"$cond": ["$motion", 1, 0]}},
            "total_leak_events": {"$sum": {"$cond": ["$leak", 1, 0]}},
            "total_door_events": {"$sum": {"$cond": ["$door", 1, 0]}},
            "record_count": {"$sum": 1}
        }}
    ]

    results = list(db.sensor_logs.aggregate(pipeline))
    if not results:
        raise HTTPException(status_code=404, detail="No data found")

    r = results[0]
    return SensorStats(
        node=node,
        period=f"{hours}h",
        avg_temperature=round(r["avg_temperature"] or 0, 2),
        avg_humidity=round(r["avg_humidity"] or 0, 2),
        avg_dust_pm25=round(r["avg_dust_pm25"] or 0, 2),
        avg_gas=round(r["avg_gas"] or 0, 2),
        max_temperature=round(r["max_temperature"] or 0, 2),
        max_gas=round(r["max_gas"] or 0, 2),
        max_dust_pm25=round(r["max_dust_pm25"] or 0, 2),
        total_motion_events=r["total_motion_events"],
        total_leak_events=r["total_leak_events"],
        total_door_events=r["total_door_events"],
        record_count=r["record_count"]
    )


# ===================== ALERTS API =====================
@app.get("/api/alerts", response_model=AlertListResponse, tags=["Alerts"])
async def get_alerts(
    limit: int = Query(default=50, ge=1, le=500),
    acknowledged: Optional[bool] = None,
    severity: Optional[str] = None,
    node: Optional[str] = None
):
    """Get recent alerts with optional filtering."""
    db = get_database()
    query: Dict[str, Any] = {}
    if acknowledged is not None:
        query["acknowledged"] = acknowledged
    if severity:
        query["severity"] = severity
    if node:
        query["node"] = node

    cursor = db.alerts.find(query).sort("created_at", -1).limit(limit)
    alerts = [serialize_doc(doc) for doc in cursor]
    total = db.alerts.count_documents(query)
    return AlertListResponse(total=total, alerts=alerts)


@app.post("/api/alerts/{alert_id}/acknowledge", response_model=AlertResponse, tags=["Alerts"])
async def acknowledge_alert(alert_id: str, ack: AlertAcknowledge):
    """Acknowledge an alert."""
    db = get_database()
    try:
        oid = ObjectId(alert_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid alert ID")

    result = db.alerts.find_one_and_update(
        {"_id": oid},
        {"$set": {
            "acknowledged": True,
            "acknowledged_by": ack.acknowledged_by,
            "acknowledged_at": datetime.utcnow()
        }},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return serialize_doc(result)


@app.delete("/api/alerts", tags=["Alerts"])
async def clear_acknowledged_alerts():
    """Delete all acknowledged alerts."""
    db = get_database()
    result = db.alerts.delete_many({"acknowledged": True})
    return {"deleted": result.deleted_count}


# ===================== INCIDENTS API =====================
@app.post("/api/incidents", response_model=IncidentResponse, tags=["Incidents"])
async def create_incident(incident: IncidentCreate):
    """Create a new incident."""
    db = get_database()
    now = datetime.utcnow()
    doc = {
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity,
        "status": "open",
        "source": incident.source,
        "sensor_reading": incident.sensor_reading,
        "created_at": now,
        "updated_at": now,
        "resolved_at": None,
        "resolved_by": None,
        "notes": []
    }
    result = db.incidents.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_doc(doc)


@app.get("/api/incidents", response_model=IncidentListResponse, tags=["Incidents"])
async def get_incidents(
    limit: int = Query(default=50, ge=1, le=200),
    status: Optional[str] = None
):
    """Get incidents."""
    db = get_database()
    query = {}
    if status:
        query["status"] = status
    cursor = db.incidents.find(query).sort("created_at", -1).limit(limit)
    incidents = [serialize_doc(doc) for doc in cursor]
    total = db.incidents.count_documents(query)
    return IncidentListResponse(total=total, incidents=incidents)


@app.patch("/api/incidents/{incident_id}", response_model=IncidentResponse, tags=["Incidents"])
async def update_incident(incident_id: str, update: IncidentUpdate):
    """Update an incident."""
    db = get_database()
    try:
        oid = ObjectId(incident_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid incident ID")

    update_data = {"updated_at": datetime.utcnow()}
    if update.status:
        update_data["status"] = update.status
        if update.status.value in ("resolved", "closed"):
            update_data["resolved_at"] = datetime.utcnow()
    if update.severity:
        update_data["severity"] = update.severity
    if update.notes:
        update_data["$push"] = {"notes": update.notes}
    if update.resolved_by:
        update_data["resolved_by"] = update.resolved_by

    result = db.incidents.find_one_and_update(
        {"_id": oid},
        {"$set": update_data},
        return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Incident not found")
    return serialize_doc(result)


# ===================== ACTIONS API =====================
class ActionRequest(BaseModel):
    action: str = Field(..., description="Action to perform: fire, flood, gas_leak, electric_leak, intrusion, temp_high, clear, reset, manual")
    priority: str = Field(default="normal", description="Priority: normal, high, critical")
    devices: Optional[Dict[str, bool]] = Field(default=None, description="Manual device states")


@app.post("/api/actions", tags=["Actions"])
async def trigger_action(action_req: ActionRequest):
    """Trigger an actuator action via MQTT."""
    listener = get_mqtt_listener()
    listener.publish_action(
        action=action_req.action,
        priority=action_req.priority,
        devices=action_req.devices
    )
    db = get_database()
    db.actuator_logs.insert_one({
        "action": action_req.action,
        "priority": action_req.priority,
        "devices": action_req.devices,
        "triggered_at": datetime.utcnow()
    })
    return {"status": "published", "action": action_req.action, "priority": action_req.priority}


# ===================== AI API =====================
@app.get("/api/ai/health", tags=["AI"])
async def get_component_health(node: str = "esp32_sensor_node"):
    """Get AI-calculated component health scores."""
    db = get_database()
    latest = db.sensor_logs.find_one({"node": node}, sort=[("timestamp", -1)])
    if not latest:
        raise HTTPException(status_code=404, detail="No sensor data available")
    predictor = get_predictor()
    predictor.add_reading(latest)
    return predictor.calculate_component_health(latest)


@app.get("/api/ai/predictions", tags=["AI"])
async def get_predictions(node: str = "esp32_sensor_node"):
    """Get AI-based predictions."""
    db = get_database()
    latest = db.sensor_logs.find_one({"node": node}, sort=[("timestamp", -1)])
    if not latest:
        raise HTTPException(status_code=404, detail="No sensor data available")

    predictor = get_predictor()
    predictor.add_reading(latest)

    return {
        "temperature_failure": predictor.predict_temperature_failure(),
        "gas_leak_trend": predictor.predict_gas_leak(),
        "maintenance_alerts": predictor.get_maintenance_alerts(),
        "component_health": predictor.calculate_component_health(latest)
    }


# ===================== WEBSOCKET =====================
@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ===================== DASHBOARD =====================
@app.get("/dashboard", response_model=HTMLResponse, tags=["Dashboard"])
async def dashboard():
    return HTMLResponse(content=_DASHBOARD_HTML, status_code=200)


# ===================== STATIC MOUNT =====================
import os
dashboard_static = os.path.join(os.path.dirname(__file__), "..", "dashboard", "static")
if os.path.exists(dashboard_static):
    app.mount("/static", StaticFiles(directory=dashboard_static), name="static")


# ===================== EMBEDDED DASHBOARD HTML =====================
_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Guardian Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --border: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --accent: #3b82f6;
            --danger: #ef4444;
            --warning: #f59e0b;
            --success: #22c55e;
            --info: #06b6d4;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
        }
        .header {
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header h1 {
            font-size: 1.5rem;
            color: var(--accent);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .status-online { background: #166534; color: #86efac; }
        .status-offline { background: #7f1d1d; color: #fca5a5; }
        .container { max-width: 1400px; margin: 0 auto; padding: 1.5rem; }
        .grid { display: grid; gap: 1rem; }
        .grid-4 { grid-template-columns: repeat(4, 1fr); }
        .grid-3 { grid-template-columns: repeat(3, 1fr); }
        .grid-2 { grid-template-columns: repeat(2, 1fr); }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 0.75rem;
            padding: 1.25rem;
        }
        .card h3 {
            font-size: 0.875rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
        }
        .metric {
            font-size: 2rem;
            font-weight: 700;
            line-height: 1;
        }
        .metric-label { font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem; }
        .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
        .mini-metric { }
        .mini-metric .value { font-size: 1.5rem; font-weight: 700; }
        .mini-metric .label { font-size: 0.75rem; color: var(--text-secondary); }
        .sensor-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
        .sensor-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            border-radius: 0.5rem;
            font-size: 0.875rem;
        }
        .sensor-item.ok { background: #14532d; }
        .sensor-item.warn { background: #78350f; }
        .sensor-item.alert { background: #7f1d1d; }
        .chart-container { height: 200px; position: relative; }
        .alerts-list { max-height: 300px; overflow-y: auto; }
        .alert-item {
            padding: 0.75rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            border-left: 4px solid;
        }
        .alert-item.emergency { border-color: var(--danger); background: rgba(239,68,68,0.1); }
        .alert-item.critical { border-color: var(--warning); background: rgba(245,158,11,0.1); }
        .alert-item.warning { border-color: var(--info); background: rgba(6,182,212,0.1); }
        .alert-item.info { border-color: var(--accent); background: rgba(59,130,246,0.1); }
        .alert-time { font-size: 0.75rem; color: var(--text-secondary); }
        .actions-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
        .action-btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.5rem;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 600;
            transition: opacity 0.2s;
        }
        .action-btn:hover { opacity: 0.8; }
        .action-btn.danger { background: var(--danger); color: white; }
        .action-btn.warning { background: var(--warning); color: black; }
        .action-btn.success { background: var(--success); color: black; }
        .action-btn.primary { background: var(--accent); color: white; }
        @media (max-width: 1024px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>AI-Guardian Dashboard</h1>
        <span id="wsStatus" class="status-badge status-offline">Connecting...</span>
    </div>
    <div class="container">
        <div class="grid grid-4" style="margin-bottom:1rem">
            <div class="card">
                <h3>Temperature</h3>
                <div class="metric" id="temperature">--</div>
                <div class="metric-label" id="tempStatus">--</div>
            </div>
            <div class="card">
                <h3>Humidity</h3>
                <div class="metric" id="humidity">--</div>
                <div class="metric-label">% Relative</div>
            </div>
            <div class="card">
                <h3>PM2.5 Dust</h3>
                <div class="metric" id="dust">--</div>
                <div class="metric-label" id="dustStatus">--</div>
            </div>
            <div class="card">
                <h3>Gas Level</h3>
                <div class="metric" id="gas">--</div>
                <div class="metric-label" id="gasStatus">--</div>
            </div>
        </div>
        <div class="grid grid-2" style="margin-bottom:1rem">
            <div class="card">
                <h3>Sensor Status</h3>
                <div class="sensor-grid">
                    <div class="sensor-item ok" id="sensor-motion"><span>Motion</span><span id="motionVal">--</span></div>
                    <div class="sensor-item ok" id="sensor-door"><span>Door</span><span id="doorVal">--</span></div>
                    <div class="sensor-item ok" id="sensor-leak"><span>Leak</span><span id="leakVal">--</span></div>
                    <div class="sensor-item ok" id="sensor-current"><span>Current Leak</span><span id="currentVal">--</span></div>
                    <div class="sensor-item ok" id="sensor-vin"><span>Input Voltage</span><span id="vinVal">--</span></div>
                    <div class="sensor-item ok" id="sensor-ups"><span>UPS Voltage</span><span id="upsVal">--</span></div>
                </div>
            </div>
            <div class="card">
                <h3>Actions</h3>
                <div class="actions-grid">
                    <button class="action-btn danger" onclick="triggerAction('fire','critical')">Fire Emergency</button>
                    <button class="action-btn warning" onclick="triggerAction('flood','critical')">Flood Emergency</button>
                    <button class="action-btn danger" onclick="triggerAction('gas_leak','critical')">Gas Leak</button>
                    <button class="action-btn danger" onclick="triggerAction('electric_leak','critical')">Electric Leak</button>
                    <button class="action-btn warning" onclick="triggerAction('intrusion','high')">Intrusion</button>
                    <button class="action-btn primary" onclick="triggerAction('clear','normal')">Clear All</button>
                    <button class="action-btn success" onclick="triggerAction('reset','normal')">Reset</button>
                </div>
            </div>
        </div>
        <div class="grid grid-2" style="margin-bottom:1rem">
            <div class="card">
                <h3>Temperature & Humidity History</h3>
                <div class="chart-container"><canvas id="tempChart"></canvas></div>
            </div>
            <div class="card">
                <h3>Gas & Dust History</h3>
                <div class="chart-container"><canvas id="gasChart"></canvas></div>
            </div>
        </div>
        <div class="card">
            <h3>Recent Alerts</h3>
            <div class="alerts-list" id="alertsList">
                <p style="color:var(--text-secondary)">No alerts yet.</p>
            </div>
        </div>
    </div>
    <script>
        const API_BASE = window.location.origin;
        let ws;
        let tempHistory = [];
        let gasHistory = [];
        const MAX_HISTORY = 30;
        let tempChart, gasChart;
        function initCharts() {
            const commonOpts = {responsive:true,maintainAspectRatio:false,animation:{duration:300},plugins:{legend:{labels:{color:'#94a3b8'}}}};
            tempChart = new Chart(document.getElementById('tempChart'), {
                type:'line',
                data:{labels:[],datasets:[
                    {label:'Temperature (C)',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.1)',fill:true,tension:0.4},
                    {label:'Humidity (%)',data:[],borderColor:'#3b82f6',backgroundColor:'rgba(59,130,246,0.1)',fill:true,tension:0.4}
                ]},
                options:{...commonOpts,scales:{'x':{grid:{color:'#334155'},ticks:{color:'#94a3b8'}},'y':{grid:{color:'#334155'},ticks:{color:'#94a3b8'}}}}
            });
            gasChart = new Chart(document.getElementById('gasChart'), {
                type:'line',
                data:{labels:[],datasets:[
                    {label:'Gas (%)',data:[],borderColor:'#f59e0b',backgroundColor:'rgba(245,158,11,0.1)',fill:true,tension:0.4},
                    {label:'PM2.5 (ug/m3)',data:[],borderColor:'#a855f7',backgroundColor:'rgba(168,85,247,0.1)',fill:true,tension:0.4}
                ]},
                options:{...commonOpts,scales:{'x':{grid:{color:'#334155'},ticks:{color:'#94a3b8'}},'y':{grid:{color:'#334155'},ticks:{color:'#94a3b8'}}}}
            });
        }
        function connectWS() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/ws/live`);
            ws.onopen = () => { document.getElementById('wsStatus').textContent = 'Live'; document.getElementById('wsStatus').className = 'status-badge status-online'; };
            ws.onclose = () => { document.getElementById('wsStatus').textContent = 'Reconnecting...'; document.getElementById('wsStatus').className = 'status-badge status-offline'; setTimeout(connectWS, 3000); };
            ws.onerror = () => ws.close();
            ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if (msg.type === 'sensor_update') updateSensorUI(msg.data);
                else if (msg.type === 'alert') addAlert(msg.data);
            };
        }
        function updateSensorUI(data) {
            document.getElementById('temperature').textContent = data.temperature?.toFixed(1) + 'C' || '--';
            document.getElementById('humidity').textContent = data.humidity?.toFixed(1) || '--';
            document.getElementById('dust').textContent = data.dust_pm25?.toFixed(1) || '--';
            document.getElementById('gas').textContent = data.gas?.toFixed(1) + '%' || '--';
            document.getElementById('tempStatus').textContent = (data.temperature > 45) ? 'WARNING' : (data.temperature > 55) ? 'CRITICAL' : 'Normal';
            document.getElementById('dustStatus').textContent = (data.dust_pm25 > 35) ? 'WARNING' : (data.dust_pm25 > 75) ? 'CRITICAL' : 'Normal';
            document.getElementById('gasStatus').textContent = (data.gas > 60) ? 'WARNING' : (data.gas > 80) ? 'CRITICAL' : 'Normal';
            document.getElementById('motionVal').textContent = data.motion ? 'YES' : 'NO';
            document.getElementById('doorVal').textContent = data.door ? 'OPEN' : 'CLOSED';
            document.getElementById('leakVal').textContent = data.leak ? 'DETECTED' : 'NONE';
            document.getElementById('currentVal').textContent = (data.current_leak || 0).toFixed(2) + 'A';
            document.getElementById('vinVal').textContent = (data.voltage_input || 0).toFixed(0) + 'V';
            document.getElementById('upsVal').textContent = (data.voltage_ups || 0).toFixed(1) + 'V';
            const el = document.getElementById('sensor-leak');
            el.className = 'sensor-item ' + (data.leak ? 'alert' : 'ok');
            const ts = new Date().toLocaleTimeString();
            tempHistory.push({t: ts, temp: data.temperature, hum: data.humidity});
            gasHistory.push({t: ts, gas: data.gas, dust: data.dust_pm25});
            if (tempHistory.length > MAX_HISTORY) tempHistory.shift();
            if (gasHistory.length > MAX_HISTORY) gasHistory.shift();
            tempChart.data.labels = tempHistory.map(h => h.t);
            tempChart.data.datasets[0].data = tempHistory.map(h => h.temp);
            tempChart.data.datasets[1].data = tempHistory.map(h => h.hum);
            tempChart.update('none');
            gasChart.data.labels = gasHistory.map(h => h.t);
            gasChart.data.datasets[0].data = gasHistory.map(h => h.gas);
            gasChart.data.datasets[1].data = gasHistory.map(h => h.dust);
            gasChart.update('none');
        }
        function addAlert(data) {
            const list = document.getElementById('alertsList');
            if (list.querySelector('p')) list.innerHTML = '';
            const item = document.createElement('div');
            item.className = 'alert-item ' + (data.severity || 'info');
            item.innerHTML = '<div><strong>' + (data.type || 'Alert') + '</strong></div><div>' + (data.message || '') + '</div><div class="alert-time">' + new Date().toLocaleString() + '</div>';
            list.prepend(item);
        }
        async function triggerAction(action, priority) {
            try {
                const res = await fetch(API_BASE + '/api/actions', {method:'POST',headers:{'Content-Type':'application/json'},body: JSON.stringify({action, priority})});
                const result = await res.json();
                console.log('Action result:', result);
            } catch (e) { console.error('Action failed:', e); }
        }
        async function loadAlerts() {
            try {
                const res = await fetch(API_BASE + '/api/alerts?limit=10');
                const data = await res.json();
                const list = document.getElementById('alertsList');
                if (data.alerts && data.alerts.length > 0) {
                    list.innerHTML = '';
                    data.alerts.forEach(a => addAlert(a));
                }
            } catch (e) { console.error('Failed to load alerts:', e); }
        }
        initCharts();
        connectWS();
        loadAlerts();
        setInterval(loadAlerts, 30000);
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
