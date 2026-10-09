from flask import Flask, render_template, send_from_directory, request, jsonify
import os, sqlite3, logging, json, random
from datetime import datetime

# === QUANTUM NEXUS v10.7 - GINOXCO SARL x VEROLIS SARL ===
# FrancoTech Cambodia 2026 - 15 Novembre 2026 - FREE FOR ALL
logging.basicConfig(level=logging.INFO, format='[QUANTUM NEXUS v10.7] %(message)s')
app = Flask(__name__, static_folder='static', static_url_path='/static')
DB_NAME = 'quantum_nexus_jury.db'  # CHANGÉ - plus sentinel_jury.db

SECTEURS = {
    "energie": {"nom": "Énergie & SNEL"},
    "eaux": {"nom": "Eaux & REGIDESO"},
    "mines": {"nom": "Mines & Extraction"},
    "securite": {"nom": "Sécurité"},
    "logistique": {"nom": "Logistique Kinshasa"},
    "agriculture": {"nom": "AgroSentinelles"},
    "sante": {"nom": "Santé & Pharma"},
    "education": {"nom": "Éducation"}
}

class HW:
    mode = "DEMO"
    ego = {"T": 26.3, "H": 52.0, "Tr_T": 0.0021, "eps": 1e-5, "led": False}
    ligo = {"imu": 0.0042, "ssr": False, "mppt": 28}
    ttd = {"eps": 1e-5, "doi": "10.5281/zenodo.19852087", "I": 1.000}

def init_db():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            secteur TEXT, 
            Tr_T REAL, 
            RC_RO REAL, 
            delta_phi REAL, 
            payload TEXT, 
            ts TEXT
        )
    """)
    con.commit()
    con.close()

init_db()

def sim():
    if HW.mode == "DEMO":
        HW.ego["T"] = round(26 + random.uniform(-0.5, 0.8), 1)
        HW.ego["H"] = round(50 + random.uniform(-2, 4), 1)
        HW.ego["Tr_T"] = round(0.0026 + random.uniform(0, 0.0005), 5) if HW.ego["led"] else round(0.0020 + random.uniform(0, 0.0003), 5)
        HW.ligo["imu"] = round(0.004 + random.uniform(-0.0005, 0.001), 5)

@app.route("/")
def home():
    sim()
    return render_template("index.html", app_version="QUANTUM NEXUS v10.7", mode=HW.mode)

@app.route("/health")
def health():
    sim()
    return jsonify({
        "status": "ok",
        "v": "10.7 QUANTUM NEXUS - FrancoTech 15 Nov 2026",
        "app": "QUANTUM NEXUS",
        "mode": HW.mode,
        "eps": 1e-5,
        "demo_pilotable": True,
        "free_jour_j": "15 Novembre 2026 - FREE FOR ALL PARTICIPANTS"
    })

@app.route("/api/ligo-box/v1")
def oracle():
    sim()
    f = float(request.args.get("f_hz", 1000))
    D = float(request.args.get("D", request.args.get("D_gpc", 1)))
    dphi = HW.ego["eps"] * (f / 100) * D
    return jsonify({
        "module": "Ligo-Box V1.2",
        "v": "10.7 QUANTUM NEXUS",
        "mode": HW.mode,
        "parametres": {
            "Tr_T": HW.ego["Tr_T"],
            "RC_RO": HW.ligo["imu"],
            "epsilon": 1e-5,
            "delta_phi_rad": dphi,
            "delta_phi_falsifiable": f"{dphi:.3e} rad",
            "doi": HW.ttd["doi"],
            "formula": "RC o RO o RI = Id + T | ||T||=eps~1e-5"
        },
        "hardware": {
            "egobox_94$": HW.ego,
            "ligobox_250$": HW.ligo
        }
    })

@app.route("/api/hardware/pilot", methods=["POST", "GET"])
def pilot():
    sim()
    if request.method == "GET":
        dev = request.args.get("device", "egobox")
        cmd = request.args.get("command", "read_all")
    else:
        j = request.get_json(silent=True) or {}
        dev = j.get("device", "egobox")
        cmd = j.get("command", "read_all")

    if "ego" in dev:
        if cmd == "led_on":
            HW.ego["led"] = True
            HW.ego["Tr_T"] += 0.0006
        elif cmd == "led_off":
            HW.ego["led"] = False
    else:
        if cmd == "ssr_on":
            HW.ligo["ssr"] = True
        elif cmd == "ssr_off":
            HW.ligo["ssr"] = False

    return jsonify({"ok": True, "mode": HW.mode, "ego": HW.ego, "ligo": HW.ligo, "app": "QUANTUM NEXUS v10.7"})

@app.route("/api/sector/<sid>", methods=["GET", "POST"])
def sector(sid):
    sim()
    if request.method == "POST":
        p = request.get_json(silent=True) or {}
        a = p.get("action", "read_all")
        if a == "led_on":
            HW.ego["led"] = True
        if a == "ssr_on":
            HW.ligo["ssr"] = True
        
        try:
            con = sqlite3.connect(DB_NAME)
            cur = con.cursor()
            cur.execute(
                "INSERT INTO telemetry (secteur, Tr_T, RC_RO, delta_phi, payload, ts) VALUES (?, ?, ?, ?, ?, ?)",
                (sid, HW.ego["Tr_T"], HW.ligo["imu"], 1e-5, json.dumps(p), datetime.now().isoformat())
            )
            con.commit()
            con.close()
        except Exception as e:
            logging.error(f"Erreur écriture DB: {e}")

        return jsonify({"ok": True, "sector": sid, "message": f"{sid} OK Tr(T)={HW.ego['Tr_T']} Mode {HW.mode} - QUANTUM NEXUS v10.7"})
    
    return jsonify({"sector": sid, "hw": HW.ego, "ligo": HW.ligo, "app": "QUANTUM NEXUS"})

@app.route("/api/ask", methods=["POST"])
def ask():
    sim()
    d = request.get_json(silent=True) or {}
    q = d.get("question", "Etat")
    f = float(d.get("f_hz", 1000))
    D = float(d.get("D_gpc", 1))
    dphi = 1e-5 * (f / 100) * D
    ans = f"Oracle QUANTUM NEXUS v10.7: Egobox {HW.ego['T']}°C Tr(T)={HW.ego['Tr_T']} Ligo [RC][RO]={HW.ligo['imu']} Δφ={dphi:.3e} Q:{q} Mode {HW.mode} I_TTD 1.000 - FrancoTech 15 Nov 2026 FREE"
    return jsonify({"answer": ans, "delta_phi": dphi})

@app.route("/manifest.json")
def mf():
    # FORCE le bon manifest.json QUANTUM NEXUS - pas de fallback SENTINEL
    if os.path.exists("manifest.json"):
        return send_from_directory(".", "manifest.json")
    else:
        return jsonify({
            "name": "QUANTUM NEXUS v10.7 — GINOXCO SARL | FrancoTech Edition",
            "short_name": "QUANTUM NEXUS v10.7",
            "start_url": "./?v=10.7",
            "display": "standalone",
            "background_color": "#020617",
            "theme_color": "#FFD43B",
            "id": "quantum-nexus-v107-francotech-15nov2026"
        })

@app.route("/sw.js")
@app.route("/service-worker.js")
def sw():
    # Sert ton nouveau service-worker.js QUANTUM NEXUS
    for filename in ["service-worker.js", "sw.js", "service_worker.js"]:
        if os.path.exists(filename):
            return send_from_directory(".", filename, mimetype="application/javascript")
    return (
        "const CACHE='quantum-nexus-v10.7-francotech-v5.0';self.addEventListener('install', e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['/'])))});self.addEventListener('activate', e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.map(k=>{if(k!==CACHE)return caches.delete(k)}))))});",
        200,
        {'Content-Type': 'application/javascript'}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))