from flask import Flask, render_template, send_from_directory, request, jsonify
import os, sqlite3, logging, json, random, math
from datetime import datetime
from werkzeug.utils import safe_join

# Logs propres Sentinel OS
logging.basicConfig(level=logging.INFO, format='[SENTINEL OS v10.6] %(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['JSON_SORT_KEYS'] = False

AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- DB SQLITE UNIFIEE ---
DB_NAME = 'sentinel_jury.db'

SECTEURS_VALIDES = {
    "energie": {"nom": "Énergie & SNEL", "statut": "Actif - Régulation Phase", "ic":"⚡", "bd":"ACTIF"},
    "eaux": {"nom": "Eaux & REGIDESO", "statut": "Actif - Débitmètre OK", "ic":"💧", "bd":"STABLE"},
    "mines": {"nom": "Mines & Extraction", "statut": "Actif - Capteurs Torsion T", "ic":"⛏️", "bd":"LIGO-BOX"},
    "securite": {"nom": "Sécurité & Surveillance", "statut": "Actif - Mode Sentinelle", "ic":"🛡️", "bd":"MODE SÉCU"},
    "logistique": {"nom": "Logistique Kinshasa", "statut": "Actif - GPS Offline", "ic":"🚚", "bd":"SYNCHRO"},
    "agriculture": {"nom": "AgroSentinelles (IoT Sols)", "statut": "Prêt - IA 98.5%", "ic":"🌱", "bd":"PRÊT"},
    "sante": {"nom": "Santé & Pharma", "statut": "Local DB - Dispensaires", "ic":"🧪", "bd":"LOCAL DB"},
    "education": {"nom": "Éducation pour Tous", "statut": "Actif - LMS Embarqué", "ic":"📚", "bd":"ACTIF"}
}

# --- ETAT HARDWARE GLOBAL - DEMO PILOTABLE MEME SANS BOX ---
class HardwareState:
    def __init__(self):
        self.mode = "DEMO"
        self.egobox = {"T":26.3,"H":52.0,"P":1012.0,"Tr_T":0.0021,"epsilon":1e-5,"led":False,"bat":100,"connected":False,"port":None}
        self.ligobox = {"imu_RC_RO":0.0042,"ssr_40A":False,"mppt_w":28.0,"lifepo4_pct":78,"pi_temp":45.2,"bme":1012}
        self.ttd = {"equation":"RC o RO o RI = Id + T, ||T||_op = epsilon","epsilon":1e-5,"doi":"10.5281/zenodo.19852087","I_TTD":1.000}

HW = HardwareState()

def init_db():
    try:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS secteurs (id TEXT PRIMARY KEY, nom TEXT, statut TEXT, last_update TEXT, data TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS telemetry (id INTEGER PRIMARY KEY AUTOINCREMENT, secteur TEXT, Tr_T REAL, RC_RO REAL, epsilon REAL, delta_phi REAL, payload TEXT, ts TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS oracle_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, question TEXT, answer TEXT, confidence TEXT, k TEXT, delta_phi REAL, ts TEXT)''')
        for sid, info in SECTEURS_VALIDES.items():
            cur.execute("INSERT OR IGNORE INTO secteurs (id,nom,statut,last_update,data) VALUES (?,?,?,?,?)", (sid, info["nom"], info["statut"], datetime.now().isoformat(), json.dumps({"ic":info["ic"],"bd":info["bd"]})) )
        con.commit(); con.close()
        logging.info("DB sentinel_jury.db init OK - Offline First")
    except Exception as e:
        logging.error(f"DB init error {e}")

init_db()

def simulate_demo():
    # Simulation DEMO pilotable même sans hardware
    if HW.mode == "DEMO":
        HW.egobox["T"] = round(26 + random.uniform(-0.5,0.8),1)
        HW.egobox["H"] = round(50 + random.uniform(-2,4),1)
        HW.egobox["P"] = round(1010 + random.uniform(0,4),1)
        if HW.egobox["led"]:
            HW.egobox["Tr_T"] = round(0.0026 + random.uniform(0,0.0006),5)
        else:
            HW.egobox["Tr_T"] = round(0.0020 + random.uniform(0,0.0003),5)
        HW.ligobox["imu_RC_RO"] = round(0.004 + random.uniform(-0.0005,0.001),5)
        HW.ligobox["mppt_w"] = round(42 + random.uniform(-2,3),1) if HW.ligobox["ssr_40A"] else round(25 + random.uniform(0,8),1))

# --- ROUTES FRONT ---
@app.route("/")
def home():
    simulate_demo()
    # Sert templates/index.html = ton v10.6 perfect
    try:
        return render_template("index.html", secteurs=SECTEURS_VALIDES, hw=HW, ttd=HW.ttd)
    except:
        # Fallback si templates/index.html pas encore remplacé
        return jsonify({"status":"SENTINEL OS v10.6 QUANTUM NEXUS MINI SUPER-INTELLIGENT OK","mode":HW.mode,"hw_demo_pilotable":True,"secteurs":list(SECTEURS_VALIDES.keys()),"ttd":HW.ttd,"endpoints":["/api/ligo-box/v1?f_hz=1000&D=1","/api/hardware/pilot","/api/sector/<id>","/api/ask","/health"]})

@app.route("/health")
def health():
    simulate_demo()
    return jsonify({"status":"ok","version":"10.6-perfect-mini-superintelligent-flask","mode":HW.mode,"offline_first":True,"epsilon":HW.ttd["epsilon"],"I_TTD":HW.ttd["I_TTD"],"hardware":{"egobox_V0.1_94$":"DEMO pilotable même sans box" if HW.mode=="DEMO" else "REEL","ligobox_V1.2_250$":"DEMO pilotable" if HW.mode=="DEMO" else "REEL","demo_pilotable":True},"ttd":HW.ttd})

@app.route("/manifest.json")
def manifest():
    if os.path.exists("manifest.json"):
        return send_from_directory(".", "manifest.json")
    return jsonify({"name":"SENTINEL OS v10.6 QUANTUM NEXUS Mini Super-Intelligent","short_name":"TTD v10.6","start_url":"/","display":"standalone","background_color":"#020617","theme_color":"#FFD43B"})

@app.route("/sw.js")
def sw():
    if os.path.exists("sw.js"):
        return send_from_directory(".", "sw.js", mimetype="application/javascript")
    return app.response_class("self.addEventListener('install',e=>{e.waitUntil(caches.open('ttd-v10.6-flask').then(c=>c.addAll(['/'])));self.skipWaiting();});self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)));});", mimetype="application/javascript")

@app.route("/static/audio/<path:filename>")
def audio(filename):
    safe_path = safe_join(AUDIO_FOLDER, filename)
    if os.path.exists(safe_path):
        return send_from_directory(AUDIO_FOLDER, filename)
    return jsonify({"error":"audio not found"}),404

# --- API TTD ORACLE - Compatible https://ttd-oracle-3lfbyz3d.onrender.com/api/ligo-box/v1 ---
@app.route("/api/ligo-box/v1")
def ligo_box():
    simulate_demo()
    f_hz = float(request.args.get("f_hz", 1000))
    D = float(request.args.get("D", request.args.get("D_gpc", 1)))
    eps = HW.egobox["epsilon"]
    tr = HW.egobox["Tr_T"]
    rc_ro = HW.ligobox["imu_RC_RO"]
    delta_phi = eps * (f_hz/100.0) * (D/1.0)  # Formule falsifiable ~1e-3 rad @1kHz/1Gpc
    # Log DB
    try:
        con=sqlite3.connect(DB_NAME); cur=con.cursor()
        cur.execute("INSERT INTO telemetry (secteur,Tr_T,RC_RO,epsilon,delta_phi,payload,ts) VALUES (?,?,?,?,?,?,?)", ("oracle",tr,rc_ro,eps,delta_phi,json.dumps({"f_hz":f_hz,"D":D}),datetime.now().isoformat()))
        con.commit(); con.close()
    except: pass
    return jsonify({
        "module":"Ligo-Box V1.2 GINOXCO","version":"10.6 Flask Mini Super-Intelligent","statut":f"Operationnel {HW.mode} pilotable même sans hardware" if HW.mode=="DEMO" else "REEL",
        "mode":HW.mode,
        "parametres":{"Tr_T":tr,"RC_RO":rc_ro,"RC_RI":rc_ro,"epsilon":eps,"delta_phi_rad":delta_phi,"delta_phi_falsifiable":f"{delta_phi:.3e} rad @ {f_hz}Hz/{D}Gpc","prediction_LIGO_O5_Dec2026":"Si O5 <1e-5 rad => TTD fausse","doi":HW.ttd["doi"],"I_TTD":HW.ttd["I_TTD"]},
        "hardware":{"egobox_V0.1_94$":{"ip65":"200x150x100mm","spirale_cu_10m_30tours":f"Tr(T)={tr} !=0","bme280":{"T":HW.egobox["T"],"H":HW.egobox["H"],"P":HW.egobox["P"]},"led":HW.egobox["led"],"powerbank_20000mAh":f"{HW.egobox['bat']}%","solar_10W":"5V"},"ligobox_V1.2_250$":{"raspberry_pi_4":HW.ligobox["pi_temp"],"imu_9axes_MPU6050_HMC5883L":f"[RC][RO]={rc_ro} !=0","ssr_40A_pyrolyse_10kg_h":HW.ligobox["ssr_40A"],"oled_0_96_epsilon":eps,"mppt_30W":f"{HW.ligobox['mppt_w']}W","lifepo4_12V_10Ah":f"{HW.ligobox['lifepo4_pct']}%"} },
        "equation_TTD":HW.ttd["equation"],"falsifiable":"Vrai test IR1 LIGO Oct/Nov 2026 + O5 Dec 2026","timestamp":datetime.now().isoformat()
    })

# --- API HARDWARE PILOT - MEME EN DEMO ---
@app.route("/api/hardware/status")
def hw_status():
    simulate_demo()
    return jsonify({"mode":HW.mode,"demo_pilotable":True,"egobox_V0.1_94$":HW.egobox,"ligobox_V1.2_250$":HW.ligobox,"ttd":HW.ttd,"instruction":"POST /api/hardware/pilot {device:'egobox',command:'led_on'} même en DEMO - jury voit pilotage sans box","ginoxco":"DG Jean Fidele LOKENDE Inox 304L CIRT 90 tours"})

@app.route("/api/hardware/mode", methods=["POST"])
def hw_mode():
    data=request.get_json(silent=True) or {}
    mode=(data.get("mode") or request.args.get("mode") or "DEMO").upper()
    if mode in ["DEMO","REEL"]: HW.mode=mode
    logging.info(f"Mode hardware {HW.mode}")
    return jsonify({"ok":True,"new_mode":HW.mode,"message":f"Mode {HW.mode} - Toujours pilotable"})

@app.route("/api/hardware/pilot", methods=["POST","GET"])
def hw_pilot():
    simulate_demo()
    if request.method=="GET":
        dev=request.args.get("device","egobox"); cmd=request.args.get("command","read_all")
    else:
        j=request.get_json(silent=True) or {}
        dev=j.get("device","egobox"); cmd=j.get("command","read_all")
    result={"status":"ok","mode":HW.mode,"device":dev,"command":cmd}
    if dev in ["egobox","ego","v0.1"]:
        if cmd=="led_on": HW.egobox["led"]=True; HW.egobox["Tr_T"]=round(HW.egobox["Tr_T"]+0.0006,5); result["action"]="LED pin13 ON - Tr(T) augmente - Détecteur T actif"
        elif cmd=="led_off": HW.egobox["led"]=False; result["action"]="LED OFF"
        elif cmd in ["read_tr","read_all"]: result["Tr_T"]=HW.egobox["Tr_T"]; result["bme280"]=HW.egobox; result["explication"]="Tr(T)!=0 via spirale Cu 10m 30 tours - Preuve TTD-02"
    elif dev in ["ligobox","ligo","v1.2","pi"]:
        if cmd=="ssr_on": HW.ligobox["ssr_40A"]=True; result["action"]="SSR 40A ON - Pyrolyse Inox 304L 10kg/h GINOXCO"
        elif cmd=="ssr_off": HW.ligobox["ssr_40A"]=False; result["action"]="SSR 40A OFF"
        elif cmd=="read_imu": result["RC_RO"]=HW.ligobox["imu_RC_RO"]; result["non_commutation"]="[RC][RO]!=0 via IMU 9 axes"
    result["egobox"]=HW.egobox; result["ligobox"]=HW.ligobox
    logging.info(f"[PILOT {HW.mode}] {dev} {cmd} -> Tr(T)={HW.egobox['Tr_T']} RC_RO={HW.ligobox['imu_RC_RO']}")
    return jsonify(result)

# --- 8 SECTEURS ---
@app.route("/api/sector/<sector_id>", methods=["GET","POST"])
def sector_api(sector_id):
    simulate_demo()
    if sector_id not in SECTEURS_VALIDES: return jsonify({"error":"secteur invalide","valid":list(SECTEURS_VALIDES.keys())}),404
    payload={}
    if request.method=="POST":
        payload=request.get_json(silent=True) or {}
        msg=payload.get("message","")[:500]
        action=payload.get("action","read_all")
        # Pilot auto selon secteur
        dev="egobox" if sector_id in ["energie","eaux","agriculture"] else "ligobox"
        if action=="led_on": HW.egobox["led"]=True
        elif action=="ssr_on": HW.ligobox["ssr_40A"]=True
        # Log DB
        try:
            con=sqlite3.connect(DB_NAME); cur=con.cursor()
            cur.execute("INSERT INTO telemetry (secteur,Tr_T,RC_RO,epsilon,delta_phi,payload,ts) VALUES (?,?,?,?,?,?,?)",(sector_id,HW.egobox["Tr_T"],HW.ligobox["imu_RC_RO"],HW.egobox["epsilon"],HW.egobox["epsilon"]*(1000/100)*1,json.dumps(payload),datetime.now().isoformat()))
            cur.execute("UPDATE secteurs SET last_update=?, data=? WHERE id=?",(datetime.now().isoformat(), json.dumps(payload), sector_id))
            con.commit(); con.close()
        except Exception as e: logging.error(e)
        return jsonify({"ok":True,"sector":sector_id,"nom":SECTEURS_VALIDES[sector_id]["nom"],"message":f"Secteur {sector_id} {SECTEURS_VALIDES