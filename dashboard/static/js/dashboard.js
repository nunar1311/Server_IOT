/**
 * AI-Guardian Dashboard JavaScript
 * Handles real-time updates via WebSocket, Chart.js, and API calls
 */

const API_BASE = window.location.origin;
const MAX_HISTORY = 40;

let tempHistory = [];
let gasHistory = [];
let tempChart, gasChart;
let wsConnected = false;

// ===================== INITIALIZATION =====================
document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    connectWebSocket();
    loadInitialData();
    setInterval(pollAlerts, 30000);
});

// ===================== CHART SETUP =====================
function initCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 200 },
        plugins: {
            legend: {
                position: "top",
                labels: {
                    color: "#94a3b8",
                    font: { size: 11 },
                    boxWidth: 12,
                    padding: 8
                }
            }
        },
        scales: {
            x: {
                grid: { color: "#334155", drawBorder: false },
                ticks: {
                    color: "#94a3b8",
                    font: { size: 10 },
                    maxTicksLimit: 8,
                    maxRotation: 0
                }
            },
            y: {
                grid: { color: "#334155", drawBorder: false },
                ticks: { color: "#94a3b8", font: { size: 10 } }
            }
        },
        elements: {
            point: { radius: 1, hoverRadius: 4 },
            line: { tension: 0.3 }
        }
    };

    tempChart = new Chart(document.getElementById("chartTempHum"), {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Temperature (C)",
                    data: [],
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239,68,68,0.08)",
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: "Humidity (%)",
                    data: [],
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.08)",
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: chartOptions
    });

    gasChart = new Chart(document.getElementById("chartGasDust"), {
        type: "line",
        data: {
            labels: [],
            datasets: [
                {
                    label: "Gas (%)",
                    data: [],
                    borderColor: "#f59e0b",
                    backgroundColor: "rgba(245,158,11,0.08)",
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: "PM2.5 (ug/m3)",
                    data: [],
                    borderColor: "#a855f7",
                    backgroundColor: "rgba(168,85,247,0.08)",
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: chartOptions
    });
}

// ===================== WEBSOCKET =====================
function connectWebSocket() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${protocol}//${location.host}/ws/live`;

    try {
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WebSocket connected");
            wsConnected = true;
            updateWsIndicator(true);
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected, reconnecting...");
            wsConnected = false;
            updateWsIndicator(false);
            setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (err) => {
            console.error("WebSocket error:", err);
            ws.close();
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "sensor_update") {
                    updateSensorUI(msg.data);
                    updateCharts(msg.data);
                } else if (msg.type === "alert") {
                    addAlertToUI(msg.data);
                }
            } catch (e) {
                console.error("Failed to parse WS message:", e);
            }
        };

        window._dashboardWs = ws;
    } catch (e) {
        console.error("WebSocket connection failed:", e);
        setTimeout(connectWebSocket, 5000);
    }
}

function updateWsIndicator(online) {
    const indicator = document.getElementById("wsIndicator");
    const text = document.getElementById("wsStatusText");
    if (online) {
        indicator.classList.add("online");
        text.textContent = "Live";
    } else {
        indicator.classList.remove("online");
        text.textContent = "Reconnecting...";
    }
}

// ===================== INITIAL DATA =====================
async function loadInitialData() {
    try {
        const [alertsRes, historyRes] = await Promise.all([
            fetch(`${API_BASE}/api/alerts?limit=20`),
            fetch(`${API_BASE}/api/sensors/history?hours=2&limit=100`)
        ]);

        if (alertsRes.ok) {
            const alertsData = await alertsRes.json();
            if (alertsData.alerts && alertsData.alerts.length > 0) {
                alertsData.alerts.forEach(addAlertToUI);
            }
        }

        if (historyRes.ok) {
            const historyData = await historyRes.json();
            if (historyData.data && historyData.data.length > 0) {
                historyData.data.forEach((d) => {
                    updateSensorUI(d);
                    updateCharts(d);
                });
            }
        }
    } catch (e) {
        console.error("Failed to load initial data:", e);
    }
}

// ===================== SENSOR UI =====================
function updateSensorUI(data) {
    const temp = data.temperature ?? data.temp;
    const hum = data.humidity ?? data.hum;
    const dust = data.dust_pm25 ?? data.dust;
    const gas = data.gas;
    const motion = data.motion;
    const door = data.door;
    const leak = data.leak;
    const current = data.current_leak ?? 0;
    const vin = data.voltage_input ?? 0;
    const ups = data.voltage_ups ?? 0;

    // Temperature
    setValue("val-temp", temp != null ? temp.toFixed(1) + "\u00b0C" : "--");
    const tempCard = document.getElementById("card-temp");
    const tempStatus = document.getElementById("status-temp");
    if (temp != null) {
        if (temp >= 55) {
            tempCard.className = "metric-card critical";
            tempStatus.textContent = "CRITICAL";
            tempStatus.className = "metric-status critical";
        } else if (temp >= 45) {
            tempCard.className = "metric-card warning";
            tempStatus.textContent = "WARNING";
            tempStatus.className = "metric-status warning";
        } else {
            tempCard.className = "metric-card";
            tempStatus.textContent = "Normal";
            tempStatus.className = "metric-status ok";
        }
    }

    // Humidity
    setValue("val-hum", hum != null ? hum.toFixed(1) + "%" : "--");
    // Dust
    setValue("val-dust", dust != null ? dust.toFixed(1) : "--");
    const dustCard = document.getElementById("card-dust");
    const dustStatus = document.getElementById("status-dust");
    if (dust != null) {
        if (dust >= 75) {
            dustCard.className = "metric-card critical";
            dustStatus.textContent = "CRITICAL";
            dustStatus.className = "metric-status critical";
        } else if (dust >= 35) {
            dustCard.className = "metric-card warning";
            dustStatus.textContent = "WARNING";
            dustStatus.className = "metric-status warning";
        } else {
            dustCard.className = "metric-card";
            dustStatus.textContent = "Normal";
            dustStatus.className = "metric-status ok";
        }
    }

    // Gas
    setValue("val-gas", gas != null ? gas.toFixed(1) + "%" : "--");
    const gasCard = document.getElementById("card-gas");
    const gasStatus = document.getElementById("status-gas");
    if (gas != null) {
        if (gas >= 80) {
            gasCard.className = "metric-card critical";
            gasStatus.textContent = "CRITICAL";
            gasStatus.className = "metric-status critical";
        } else if (gas >= 60) {
            gasCard.className = "metric-card warning";
            gasStatus.textContent = "WARNING";
            gasStatus.className = "metric-status warning";
        } else {
            gasCard.className = "metric-card";
            gasStatus.textContent = "Normal";
            gasStatus.className = "metric-status ok";
        }
    }

    // Sensor badges
    updateBadge("badge-motion", motion ? "DETECTED" : "Clear", motion ? "active" : "ok");
    updateBadge("badge-door", door ? "OPEN" : "Closed", door ? "alert" : "ok");
    updateBadge("badge-leak", leak ? "LEAK!" : "None", leak ? "alert" : "ok");

    // Values
    setValue("val-current", current.toFixed(2) + " A");
    setValue("val-vin", vin.toFixed(0) + " V");
    setValue("val-ups", ups.toFixed(1) + " V");
}

function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateBadge(id, text, state) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = text;
        el.className = "sensor-badge " + state;
    }
}

// ===================== CHARTS =====================
function updateCharts(data) {
    const temp = data.temperature ?? data.temp;
    const hum = data.humidity ?? data.hum;
    const dust = data.dust_pm25 ?? data.dust;
    const gas = data.gas;
    const now = new Date().toLocaleTimeString();

    if (temp != null && hum != null) {
        tempHistory.push({ t: now, temp, hum });
        if (tempHistory.length > MAX_HISTORY) tempHistory.shift();
        tempChart.data.labels = tempHistory.map((h) => h.t);
        tempChart.data.datasets[0].data = tempHistory.map((h) => h.temp);
        tempChart.data.datasets[1].data = tempHistory.map((h) => h.hum);
        tempChart.update("none");
    }

    if (gas != null && dust != null) {
        gasHistory.push({ t: now, gas, dust });
        if (gasHistory.length > MAX_HISTORY) gasHistory.shift();
        gasChart.data.labels = gasHistory.map((h) => h.t);
        gasChart.data.datasets[0].data = gasHistory.map((h) => h.gas);
        gasChart.data.datasets[1].data = gasHistory.map((h) => h.dust);
        gasChart.update("none");
    }
}

// ===================== ALERTS =====================
function addAlertToUI(alert) {
    const container = document.getElementById("alertsContainer");
    const noData = container.querySelector(".no-data");
    if (noData) noData.remove();

    const severity = alert.severity || "info";
    const time = alert.created_at
        ? new Date(alert.created_at).toLocaleString()
        : new Date().toLocaleString();

    const item = document.createElement("div");
    item.className = `alert-item ${severity}`;
    item.innerHTML = `
        <div style="flex:1">
            <div class="alert-type">${escapeHtml(alert.type || "Alert")}</div>
            <div class="alert-message">${escapeHtml(alert.message || "")}</div>
            <div class="alert-time">${time}</div>
        </div>
        <span class="alert-severity ${severity}">${severity.toUpperCase()}</span>
    `;

    container.insertBefore(item, container.firstChild);

    while (container.children.length > 30) {
        container.removeChild(container.lastChild);
    }
}

async function pollAlerts() {
    try {
        const res = await fetch(`${API_BASE}/api/alerts?limit=5`);
        if (res.ok) {
            const data = await res.json();
            if (data.alerts && data.alerts.length > 0 && wsConnected) {
                data.alerts.slice(0, 3).forEach(addAlertToUI);
            }
        }
    } catch (e) {
        console.error("Failed to poll alerts:", e);
    }
}

// ===================== ACTIONS =====================
async function triggerAction(action, priority) {
    try {
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = "...";
        btn.disabled = true;

        const res = await fetch(`${API_BASE}/api/actions`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action, priority })
        });

        const result = await res.json();
        console.log("Action result:", result);

        btn.textContent = "OK!";
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 1500);
    } catch (e) {
        console.error("Action failed:", e);
        if (event.target) {
            event.target.textContent = "Error";
            event.target.disabled = false;
        }
    }
}

// ===================== UTILITIES =====================
function escapeHtml(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
