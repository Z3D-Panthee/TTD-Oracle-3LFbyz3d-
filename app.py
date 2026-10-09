"""QUANTUM NEXUS v10.8.1c — Flask FIX TEMPLATES - FrancoTech FREE"""
from datetime import datetime, timezone
from pathlib import Path
import logging
import os
import random
import sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SENTINEL_DB_PATH", str(BASE_DIR / "quantum_nexus_jury.db")))

logging.basicConfig(level="INFO", format="[QN v10.8.1c] %(message)s")
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

FRANCOTECH_APPS = {
    "true_north_rc": {"id": "true_north_rc", "nom": "TRUE NORTH RC", "subtitle": "Remote Control & Navigation", "desc": "Monitoring en temps réel", "icone": "🧭", "color": "#00eaff", "version": "v1.0 FREE", "hardware": "GPS 90$ + ESP32"},
    "supervpn_ro": {"id": "supervpn_ro", "nom": "SUPERVPN RO", "subtitle": "VPN Sécurisé RO", "desc": "Connexion chiffrée", "icone": "🔒", "color": "#238cff", "version": "v1.0 FREE", "hardware": "AES-256-GCM"},
    "vault_ri": {"id": "vault_ri", "nom": "VAULT RI", "subtitle": "Coffre-fort Numérique RI", "desc": "Stockage chiffré", "icone": "🏦", "color": "#ffd166", "version": "v1.0 FREE", "hardware": "SQLite chiffré"}
}

HW = {
    "mode": "DEMO",
    "ego": {"T": 26.3, "H": 52.0, "Tr_T": 0.0021, "eps": 1e-5, "led": False, "gps": "-4.325°S 15.322°E LEMBA"},
    "ligo": {"imu": 0.0042, "ssr": False, "mppt": 28, "ip": "10.8.0.2"},
    "ttd": {"eps": 1e-5, "doi": "10.5281/zenodo.19852087", "I": 1.000}
}

def now(): return datetime.now(timezone.utc).isoformat()
def get_db():
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    return con
def init_db():
    try:
        with get_db() as con:
            con.execute("CREATE TABLE IF NOT EXISTS telemetry(id INTEGER PRIMARY KEY AUTOINCREMENT, secteur TEXT, Tr_T REAL, RC_RO REAL, delta_phi REAL, payload TEXT, ts TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, details TEXT DEFAULT '', ts TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS vault_ri(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, encrypted INTEGER DEFAULT 1, size_kb INTEGER, ts TEXT)")
            cur = con.execute("SELECT COUNT(*) as c FROM vault_ri").fetchone()
            if cur["c"] == 0:
                for f in [("rapport_snel_15nov.pdf",245),("gps_lemba_logs.enc",128),("francotech_inscription.json",12)]:
                    con.execute("INSERT INTO vault_ri(filename,size_kb,ts) VALUES(?,?,?)",(f[0],f[1],now()))
            con.commit()
    except Exception as e: logger.error(f"DB init error: {e}")
def log_event(event, details=""):
    try:
        with get_db() as con:
            con.execute("INSERT INTO events(event,details,ts) VALUES(?,?,?)",(event,details[:2000],now()))
            con.commit()
    except: pass
def simulate():
    HW["ego"]["T"] = round(26+random.uniform(-0.5,0.8),1)
    HW["ego"]["Tr_T"] = round(0.0020+random.uniform(0,0.0005),5)
    HW["ligo"]["imu"] = round(0.004+random.uniform(-0.0005,0.001),5)
    HW["ego"]["gps"] = f"{-4.325+random.uniform(-0.01,0.01):.3f}°S {15.322+random.uniform(-0.01,0.01):.3f}°E LEMBA LIVE"
    HW["ligo"]["ip"] = f"10.8.0.{random.randint(2,20)}"

init_db()

# === FIX PRINCIPAL : Supporte templates/index.html ===
def find_and_serve(filename, mimetype=None):
    search_dirs = [BASE_DIR, BASE_DIR/"templates", BASE_DIR/"static", BASE_DIR/"templates"/"static"]
    for d in search_dirs:
        fp = d / filename
        if fp.exists():
            return send_from_directory(d, filename, mimetype=mimetype) if mimetype else send_from_directory(d, filename)
    return None

@app.get("/")
def home():
    res = find_and_serve("index.html")
    if res: return res
    return jsonify(status="QUANTUM NEXUS v10.8.1c online - index.html manquant", searched=[str(BASE_DIR), str(BASE_DIR/"templates")])

@app.get("/manifest.json")
def manifest():
    res = find_and_serve("manifest.json", mimetype="application/manifest+json")
    if res: return res
    return jsonify(name="QUANTUM NEXUS v10.8.1", short_name="QN v10.8.1")

@app.get("/sw.js")
@app.get("/service-worker.js")
def sw():
    for name in ["sw.js","service-worker.js"]:
        res = find_and_serve(name, mimetype="application/javascript")
        if res: return res
    return ("",204)

@app.get("/api/sectors")
def sectors(): return jsonify([{"id":k,**v} for k,v in SECTEURS.items()])

@app.get("/api/ligo-box/v1")
def oracle():
    simulate()
    f_hz=float(request.args.get("f_hz",1000)); D=float(request.args.get("D_gpc",1))
    dphi=HW["ttd"]["eps"]*(f_hz/100)*D
    return jsonify(module="Ligo-Box V1.2", version="10.8.1c", parametres={"Tr_T":HW["ego"]["Tr_T"],"RC_RO":HW["ligo"]["imu"],"epsilon":HW["ttd"]["eps"],"delta_phi_rad":dphi,"doi":HW["ttd"]["doi"]}, hardware=HW, timestamp=now())

@app.route("/api/hardware/pilot", methods=["GET","POST"])
def pilot():
    simulate(); data=request.get_json(silent=True) or request.args
    device=str(data.get("device","egobox")); command=str(data.get("command","read_all"))
    if device=="egobox" and command in {"led_on","led_off"}: HW["ego"]["led"]=(command=="led_on")
    if device=="ligobox" and command in {"ssr_on","ssr_off"}: HW["ligo"]["ssr"]=(command=="ssr_on")
    return jsonify(ok=True, ego=HW["ego"], ligo=HW["ligo"], timestamp=now())

@app.get("/api/francotech/apps")
def francotech_apps():
    simulate()