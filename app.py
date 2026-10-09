"""Sentinel OS / QUANTUM NEXUS v10.8.1 — Flask demo backend + FrancoTech 15 Nov 2026 FREE
All hardware values are simulated until a real driver is configured.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import logging
import os
import random
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SENTINEL_DB_PATH", str(BASE_DIR / "quantum_nexus_jury.db")))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="[QUANTUM NEXUS v10.8.1] %(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False

SECTEURS = {
    "energie": {"nom": "Énergie & SNEL", "icone": "⚡"},
    "eaux": {"nom": "Eaux & REGIDESO", "icone": "💧"},
    "mines": {"nom": "Mines & extraction", "icone": "⛏️"},
    "securite": {"nom": "Sécurité", "icone": "🛡️"},
    "logistique": {"nom": "Logistique", "icone": "🚚"},
    "agriculture": {"nom": "AgroSentinelles", "icone": "🌱"},
    "sante": {"nom": "Santé & pharma", "icone": "🧪"},
    "education": {"nom": "Éducation", "icone": "📚"}
}

# === 3 APPS FRANCOTECH 15 NOV 2026 - FREE FOR ALL ===
FRANCOTECH_APPS = {
    "true_north_rc": {
        "id": "true_north_rc",
        "nom": "TRUE NORTH RC",
        "subtitle": "Remote Control & Navigation",
        "desc": "Monitoring en temps réel - Géolocalisation sécurisée",
        "icone": "🧭",
        "color": "#00eaff",
        "version": "v1.0 FREE",
        "hardware": "GPS Tracker 90$ + ESP32"
    },
    "supervpn_ro": {
        "id": "supervpn_ro",
        "nom": "SUPERVPN RO",
        "subtitle": "VPN Sécurisé RO",
        "desc": "Connexion chiffrée - Accès réseau protégé",
        "icone": "🔒",
        "color": "#238cff",
        "version": "v1.0 FREE",
        "hardware": "AES-256-GCM + Tunnel"
    },
    "vault_ri": {
        "id": "vault_ri",
        "nom": "VAULT RI",
        "subtitle": "Coffre-fort Numérique RI",
        "desc": "Stockage chiffré - Sauvegarde résiliente",
        "icone": "🏦",
        "color": "#ffd166",
        "version": "v1.0 FREE",
        "hardware": "SQLite chiffré + AES"
    }
}

HW = {
    "mode": "DEMO",
    "ego": {"T": 26.3, "H": 52.0, "Tr_T": 0.0021, "eps": 1e-5, "led": False, "gps": "-4.325°S 15.322°E LEMBA"},
    "ligo": {"imu": 0.0042, "ssr": False, "mppt": 28, "ip": "10.8.0.2"},
    "ttd": {"eps": 1e-5, "doi": "10.5281/zenodo.19852087", "I": 1.000}
}

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def get_db():
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    try:
        with get_db() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS telemetry(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    secteur TEXT NOT NULL,
                    Tr_T REAL,
                    RC_RO REAL,
                    delta_phi REAL,
                    payload TEXT NOT NULL,
                    ts TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS events(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    details TEXT NOT NULL DEFAULT '',
                    ts TEXT NOT NULL
                )
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS vault_ri(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    encrypted INTEGER DEFAULT 1,
                    size_kb INTEGER,
                    ts TEXT NOT NULL
                )
            """)
            # Seed vault avec 3 fichiers exemple
            cur = con.execute("SELECT COUNT(*) as c FROM vault_ri").fetchone()
            if cur["c"] == 0:
                for f in [("rapport_snel_15nov.pdf", 245), ("gps_lemba_logs.enc", 128), ("francotech_inscription.json", 12)]:
                    con.execute("INSERT INTO vault_ri(filename,size_kb,ts) VALUES(?,?,?)", (f[0], f[1], now()))
            con.commit()
        logger.info("Base QUANTUM NEXUS v10.8.1 initialisée.")
    except Exception as e:
        logger.error(f"Erreur init DB : {e}")

def log_event(event: str, details: str = ""):
    try:
        with get_db() as con:
            con.execute("INSERT INTO events(event, details, ts) VALUES(?,?,?)", (event, details[:2000], now()))
            con.commit()
    except Exception as e:
        logger.error(f"Erreur events : {e}")

def simulate():
    if HW["mode"] == "DEMO":
        HW["ego"]["T"] = round(26 + random.uniform(-0.5, 0.8), 1)
        HW["ego"]["H"] = round(50 + random.uniform(-2, 4), 1)
        HW["ego"]["Tr_T"] = round((0.0026 if HW["ego"]["led"] else 0.0020) + random.uniform(0, 0.0003), 5)
        HW["ligo"]["imu"] = round(0.004 + random.uniform(-0.0005, 0.001), 5)
        HW["ego"]["gps"] = f"{-4.325+random.uniform(-0.01,0.01):.3f}°S {15.322+random.uniform(-0.01,0.01):.3f}°E LEMBA LIVE"
        HW["ligo"]["ip"] = f"10.8.0.{random.randint(2,20)}"

init_db()

@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.get("/health")
def health():
    return jsonify(
        status="ok",
        version="10.8.1",
        application="QUANTUM NEXUS v10.7 / Sentinel OS — FrancoTech 15 Nov 2026 FREE FOR ALL",
        mode=HW["mode"],
        hardware="SIMULATED_UNLESS_CONFIGURED",
        francotech="2026-11-15 Koh Pich - FREE FOR ALL PARTICIPANTS - 100% GRATUIT JOUR J",
        timestamp=now()
    )

@app.get("/manifest.json")
def manifest():
    return send_from_directory(BASE_DIR, "manifest.json", mimetype="application/manifest+json")

@app.get("/sw.js")
@app.get("/service-worker.js")
def sw():
    for fn in ["service-worker.js", "sw.js"]:
        if (BASE_DIR / fn).exists():
            return send_from_directory(BASE_DIR, fn, mimetype="application/javascript")
    return send_from_directory(BASE_DIR, "sw.js", mimetype="application/javascript")

# === EXISTANT : secteurs, ligo-box, pilot etc ===
@app.get("/api/sectors")
def sectors():
    return jsonify([{"id": k, **v} for k, v in SECTEURS.items()])

@app.get("/api/ligo-box/v1")
def oracle():
    simulate()
    try:
        f_hz = max(0.0, min(float(request.args.get("f_hz", 1000)), 1e9))
        distance = max(0.0, min(float(request.args.get("D_gpc", 1)), 1e6))
    except (TypeError, ValueError):
        return jsonify(error="f_hz et D_gpc doivent être des valeurs numériques valides"), 400
    dphi = HW["ego"]["eps"] * (f_hz / 100) * distance
    return jsonify(
        module="Ligo-Box V1.2",
        version="10.8.1 QUANTUM NEXUS",
        mode=HW["mode"],
        parametres={"Tr_T": HW["ego"]["Tr_T"], "RC_RO": HW["ligo"]["imu"], "epsilon": HW["ttd"]["eps"], "delta_phi_rad": dphi, "doi": HW["ttd"]["doi"], "formula": "RC o RO o RI = Id + T | ε=1e-5"},
        hardware={"egobox": HW["ego"], "ligobox": HW["ligo"]},
        timestamp=now()
    )

@app.route("/api/hardware/pilot", methods=["GET", "POST"])
def pilot():
    simulate()
    data = request.get_json(silent=True) or request.args
    device = str(data.get("device", "egobox"))
    command = str(data.get("command", "read_all"))
    if device not in {"egobox", "ligobox"}:
        return jsonify(error="device doit être 'egobox' ou 'ligobox'"), 400
    if command not in {"read_all", "led_on", "led_off", "ssr_on", "ssr_off"}:
        return jsonify(error="Commande inconnue"), 400
    if device == "egobox" and command in {"led_on", "led_off"}:
        HW["ego"]["led"] = (command == "led_on")
    elif device == "ligobox" and command in {"ssr_on", "ssr_off"}:
        HW["ligo"]["ssr"] = (command == "ssr_on")
    else:
        command = "read_all"
    log_event("COMMANDE_DEMO", f"{device}:{command}")
    return jsonify(ok=True, mode=HW["mode"], hardware="SIMULATED", ego=HW["ego"], ligo=HW["ligo"], timestamp=now())

@app.route("/api/sector/<sid>", methods=["GET", "POST"])
def sector(sid):
    if sid not in SECTEURS:
        return jsonify(error="Secteur inconnu", sectors=list(SECTEURS.keys())), 404
    simulate()
    payload = request.get_json(silent=True) or {}
    action = str(payload.get("action", "read_all"))
    if request.method == "POST":
        if action not in {"read_all", "led_on", "led_off", "ssr_on", "ssr_off"}:
            return jsonify(error="Action inconnue"), 400
        if action in {"led_on", "led_off"}:
            HW["ego"]["led"] = (action == "led_on")
        if action in {"ssr_on", "ssr_off"}:
            HW["ligo"]["ssr"] = (action == "ssr_on")
        try:
            with get_db() as con:
                con.execute("INSERT INTO telemetry(secteur, Tr_T, RC_RO, delta_phi, payload, ts) VALUES(?,?,?,?,?,?)",
                    (sid, HW["ego"]["Tr_T"], HW["ligo"]["imu"], HW["ttd"]["eps"], json.dumps(payload, ensure_ascii=False), now()))
                con.commit()
        except Exception as e:
            logger.error(f"Erreur télémétrie : {e}")
        log_event("SECTEUR", f"{sid}:{action}")
    return jsonify(ok=True, sector=sid, nom=SECTEURS[sid]["nom"], mode=HW["mode"], hardware="SIMULATED", hw=HW["ego"], ligo=HW["ligo"], timestamp=now())

@app.post("/api/ask")
def ask():
    simulate()
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "État général"))[:500]
    try:
        f_hz = max(0.0, min(float(data.get("f_hz", 1000)), 1e9))
        distance = max(0.0, min(float(data.get("D_gpc", 1)), 1e6))
    except (TypeError, ValueError):
        return jsonify(error="f_hz et D_gpc doivent être des valeurs numériques valides"), 400
    dphi = HW["ttd"]["eps"] * (f_hz / 100) * distance
    answer = f"Oracle QUANTUM NEXUS v10.8.1 (mode {HW['mode']}) — Q: {question}. T={HW['ego']['T']}°C Tr(T)={HW['ego']['Tr_T']} IMU={HW['ligo']['imu']} Δφ={dphi:.3e} rad I_TTD={HW['ttd']['I']:.3f}. FREE 15 Nov 2026 FrancoTech."
    log_event("ORACLE_QUESTION", question)
    return jsonify(answer=answer, delta_phi=dphi, mode=HW["mode"], hardware="SIMULATED", timestamp=now())

@app.get("/api/telemetry")
def telemetry():
    limit = max(1, min(request.args.get("limit", 50, type=int) or 50, 200))
    try:
        with get_db() as con:
            data = [dict(r) for r in con.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT?", (limit,)).fetchall()]
        return jsonify(data)
    except Exception as e:
        return jsonify(error=f"Erreur télémétrie : {str(e)}"), 500

# === NOUVEAU : 3 APPS FRANCOTECH DASHBOARD ===
@app.get("/api/francotech/apps")
def francotech_apps():
    """Liste des 3 apps poster pour le tableau de bord"""
    simulate()
    return jsonify(
        event="FrancoTech Koh Pich - 15 Novembre 2026 - FREE FOR ALL - 100% GRATUIT JOUR J",
        date="15 Novembre 2026",
        lieu="Koh Pich Convention Center - Phnom Penh",
        version="QUANTUM NEXUS v10.7 - Tableau de bord",
        apps=[{"id": k, **v, "live": HW["ego"] if "rc" in k else HW["ligo"] if "ro" in k else {"files": 3}} for k, v in FRANCOTECH_APPS.items()],
        timestamp=now()
    )

@app.route("/api/rc/control", methods=["GET","POST"])
def rc_control():
    """TRUE NORTH RC - Remote Control & Navigation"""
    simulate()
    data = request.get_json(silent=True) or request.args
    action = str(data.get("action", "status"))
    log_event("TRUE_NORTH_RC", action)
    return jsonify(
        app="TRUE NORTH RC",
        id="true_north_rc",
        status="Monitoring en temps réel ACTIF",
        gps=HW["ego"]["gps"],
        action=action,
        telemetry={"T": HW["ego"]["T"], "Tr_T": HW["ego"]["Tr_T"], "led": HW["ego"]["led"]},
        hardware="GPS Tracker 90$ + ESP32 + Egobox 94$",
        timestamp=now()
    )

@app.route("/api/ro/vpn", methods=["GET","POST"])
def ro_vpn():
    """SUPERVPN RO - VPN Sécurisé"""
    simulate()
    log_event("SUPERVPN_RO", "vpn_activate")
    return jsonify(
        app="SUPERVPN RO",
        id="supervpn_ro",
        status="Connexion chiffrée - Accès réseau protégé",
        tunnel="AES-256-GCM",
        ip_local="192.168.1.10",
        ip_vpn=HW["ligo"]["ip"],
        latency_ms=round(random.uniform(8, 24), 1),
        hardware="VPN Sécurisé RO - Ligo-Box 250$",
        timestamp=now()
    )

@app.route("/api/ri/vault", methods=["GET","POST"])
def ri_vault():
    """VAULT RI - Coffre-fort Numérique"""
    simulate()
    try:
        with get_db() as con:
            files = [dict(r) for r in con.execute("SELECT * FROM vault_ri ORDER BY id DESC").fetchall()]
            count = len(files)
    except Exception:
        files = []
        count = 3
    log_event("VAULT_RI", f"vault_open {count} files")
    return jsonify(
        app="VAULT RI",
        id="vault_ri",
        status="Stockage chiffré - Sauvegarde résiliente",
        files_count=count,
        files=files,
        encryption="AES-256 + SQLite chiffré",