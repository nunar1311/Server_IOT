// AI-Guardian - MongoDB Initialization Script
// Creates users, databases, and initial collections with indexes

// Create application user
db.createUser({
    user: "ai_guardian_app",
    pwd: "app_secure_password_2024",
    roles: [
        { role: "readWrite", db: "ai_guardian" },
        { role: "dbAdmin", db: "ai_guardian" }
    ]
});

// Switch to ai_guardian database
db = db.getSiblingDB("ai_guardian");

// --- sensor_logs collection ---
db.createCollection("sensor_logs");
db.sensor_logs.createIndex({ "timestamp": -1 });
db.sensor_logs.createIndex({ "node": 1, "timestamp": -1 });
db.sensor_logs.createIndex({ "temperature": 1 });
db.sensor_logs.createIndex({ "gas": 1 });
db.sensor_logs.createIndex({ "leak": 1 });
db.sensor_logs.createIndex({ "motion": 1 });

// --- alerts collection ---
db.createCollection("alerts");
db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "severity": 1, "timestamp": -1 });
db.alerts.createIndex({ "type": 1, "timestamp": -1 });
db.alerts.createIndex({ "acknowledged": 1, "timestamp": -1 });

// --- incidents collection ---
db.createCollection("incidents");
db.incidents.createIndex({ "created_at": -1 });
db.incidents.createIndex({ "status": 1, "created_at": -1 });
db.incidents.createIndex({ "severity": 1 });

// --- actuator_logs collection ---
db.createCollection("actuator_logs");
db.actuator_logs.createIndex({ "timestamp": -1 });
db.actuator_logs.createIndex({ "action": 1, "timestamp": -1 });

// --- camera_alerts collection ---
db.createCollection("camera_alerts");
db.camera_alerts.createIndex({ "timestamp": -1 });
db.camera_alerts.createIndex({ "alert_type": 1, "timestamp": -1 });
db.camera_alerts.createIndex({ "node": 1, "timestamp": -1 });

// --- settings collection ---
db.createCollection("settings");
db.settings.insertOne({
    _id: "system",
    name: "AI-Guardian System",
    version: "1.0.0",
    thresholds: {
        temperature: { warning: 45, critical: 55 },
        humidity: { warning: 80, critical: 90 },
        dust_pm25: { warning: 35, critical: 75 },
        gas: { warning: 60, critical: 80 },
        current_leak: { warning: 3, critical: 5 },
        voltage_low: { warning: 200, critical: 180 }
    },
    rules: {
        auto_response: true,
        alert_cooldown_seconds: 60,
        camera_detection_enabled: true,
        telegram_enabled: false
    },
    created_at: new Date(),
    updated_at: new Date()
});

// --- system_stats collection (for analytics) ---
db.createCollection("system_stats");
db.system_stats.createIndex({ "date": -1 });
db.system_stats.createIndex({ "node": 1, "date": -1 });

print("AI-Guardian MongoDB initialized successfully!");
