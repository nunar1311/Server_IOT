# ============================================================
# AI-Guardian - Flask Dashboard Application
# Co the chay doc lap hoac tich hop voi backend
# ============================================================

from flask import Flask, render_template, jsonify, request, Response
from flask_cors import CORS
import pymongo
import json
import datetime
import paho.mqtt.client as mqtt
from threading import Thread
import os
import time

app = Flask(__name__, template_folder='../dashboard/templates', static_folder='../dashboard/static')
CORS(app)

# MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:ai_guardian_secure_pass_2024@localhost:27017")
DB_NAME = "ai_guardian"
mongo_client = pymongo.MongoClient(MONGODB_URL)
db = mongo_client[DB_NAME]

# MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883)
mqtt_client.loop_start()

# ===================== ROUTES =====================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_data():
    latest = db.sensor_logs.find_one(sort=[("timestamp", pymongo.DESCENDING)])
    recent_alerts = list(db.alerts.find().sort("created_at", pymongo.DESCENDING).limit(10))
    recent_incidents = list(db.incidents.find().sort("created_at", pymongo.DESCENDING).limit(5))

    stats_24h = db.sensor_logs.aggregate([
        {"$match": {"timestamp": {"$gte": datetime.datetime.utcnow() - datetime.timedelta(hours=24)}}},
        {"$group": {
            "_id": None,
            "avg_temp": {"$avg": "$temperature"},
            "avg_hum": {"$avg": "$humidity"},
            "avg_gas": {"$avg": "$gas"},
            "max_temp": {"$max": "$temperature"},
            "max_gas": {"$max": "$gas"}
        }}
    ])
    stats = list(stats_24h)

    return jsonify({
        "latest": latest,
        "alerts": recent_alerts,
        "incidents": recent_incidents,
        "stats": stats[0] if stats else {}
    })


@app.route("/api/actions", methods=["POST"])
def trigger_action():
    data = request.json
    action = data.get("action", "unknown")
    priority = data.get("priority", "normal")

    payload = json.dumps({
        "action": action,
        "priority": priority,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })
    mqtt_client.publish("ai-guardian/actions", payload)

    db.actuator_logs.insert_one({
        "action": action,
        "priority": priority,
        "triggered_at": datetime.datetime.utcnow()
    })

    return jsonify({"status": "published", "action": action})


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    limit = request.args.get("limit", 50, type=int)
    alerts = list(db.alerts.find().sort("created_at", pymongo.DESCENDING).limit(limit))
    for a in alerts:
        a["_id"] = str(a["_id"])
    return jsonify(alerts)


@app.route("/api/alerts/<alert_id>/acknowledge", methods=["POST"])
def acknowledge_alert(alert_id):
    db.alerts.update_one(
        {"_id": pymongo.ObjectId(alert_id)},
        {"$set": {
            "acknowledged": True,
            "acknowledged_at": datetime.datetime.utcnow()
        }}
    )
    return jsonify({"status": "acknowledged"})


@app.route("/api/sensors/history", methods=["GET"])
def sensor_history():
    hours = request.args.get("hours", 24, type=int)
    since = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
    data = list(db.sensor_logs.find(
        {"timestamp": {"$gte": since}}
    ).sort("timestamp", pymongo.ASCENDING).limit(500))
    for d in data:
        d["_id"] = str(d["_id"])
    return jsonify(data)


@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        mongo_client.admin.command("ping")
        mqtt_status = "connected" if mqtt_client.is_connected() else "disconnected"
        return jsonify({
            "status": "healthy",
            "mongodb": "connected",
            "mqtt": mqtt_status,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }), 500


# ===================== SSE (Server-Sent Events) =====================
clients = []

@app.route("/api/stream")
def stream():
    def generate():
        client_id = str(time.time())
        clients.append(client_id)
        try:
            while True:
                latest = db.sensor_logs.find_one(sort=[("timestamp", pymongo.DESCENDING)])
                if latest:
                    latest["_id"] = str(latest["_id"])
                    yield f"data: {json.dumps(latest)}\n\n"
                time.sleep(1)
        except GeneratorExit:
            pass
        finally:
            clients.remove(client_id)
    return Response(generate(), mimetype="text/event-stream")


# ===================== MAIN =====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
