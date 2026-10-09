"""Sentinel OS / TTD Oracle — Flask demo backend.
All hardware values are simulated until a real driver is configured.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, logging, os, random, sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SENTINEL_DB_PATH", str(BASE_DIR / "sentinel_jury.db")))
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="[SENTINEL OS] %(levelname)s %(message)s")
app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False
SECTEURS = {
    "energie": {"nom":"Énergie & SNEL", "icone":"⚡"}, "eaux":{"nom":"Eaux & REGIDESO", "icone":"💧"},
    "mines":{"nom":"Mines & extraction", "icone":"⛏️"}, "securite":{"nom":"Sécurité", "icone":"🛡️"},
    "logistique":{"nom":"Logistique", "icone":"🚚"}, "agriculture":{"nom":"AgroSentinelles", "icone":"🌱"},
    "sante":{"nom":"Santé & pharma", "icone":"🧪"}, "education":{"nom":"Éducation", "icone":"📚"}}
HW = {"mode":"DEMO", "ego":{"T":26.3,"H":52.0,"Tr_T":0.0021,"eps":1e-5,"led":False}, "ligo":{"imu":0.0042,"ssr":False,"mppt":28}, "ttd":{"eps":1e-5,"doi":"10.5281/zenodo.19852087","I":1.000}}

def now(): return datetime.now(timezone.utc).isoformat()
def db():
    con=sqlite3.connect(DB_PATH,timeout=15); con.row_factory=sqlite3.Row; return con
def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS telemetry(id INTEGER PRIMARY KEY AUTOINCREMENT, secteur TEXT NOT NULL, Tr_T REAL, RC_RO REAL, delta_phi REAL, payload TEXT NOT NULL, ts TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, details TEXT NOT NULL DEFAULT '', ts TEXT NOT NULL)""")
def log_event(event, details=""):
    with db() as con: con.execute("INSERT INTO events(event,details,ts) VALUES(?,?,?)",(event,details[:2000],now()))
def simulate():
    if HW["mode"] == "DEMO":
        HW["ego"]["T"] = round(26+random.uniform(-0.5,0.8),1)
        HW["ego"]["H"] = round(50+random.uniform(-2,4),1)
        HW["ego"]["Tr_T"] = round((0.0026 if HW["ego"]["led"] else 0.0020)+random.uniform(0,0.0003),5)
        HW["ligo"]["imu"] = round(0.004+random.uniform(-0.0005,0.001),5)

@app.get("/")
def home(): return send_from_directory(BASE_DIR,"index.html")
@app.get("/health")
def health(): return jsonify(status="ok",version="10.8",application="Sentinel OS / TTD Oracle",mode=HW["mode"],hardware="SIMULATED_UNLESS_CONFIGURED",timestamp=now())
@app.get("/manifest.json")
def manifest(): return send_from_directory(BASE_DIR,"manifest.json",mimetype="application/manifest+json")
@app.get("/sw.js")
def sw(): return send_from_directory(BASE_DIR,"sw.js",mimetype="application/javascript")
@app.get("/api/sectors")
def sectors(): return jsonify([{ "id":k, **v} for k,v in SECTEURS.items()])
@app.get("/api/ligo-box/v1")
def oracle():
    simulate()
    try: f=max(0.0,min(float(request.args.get("f_hz",1000)),1e9)); distance=max(0.0,min(float(request.args.get("D_gpc",1)),1e6))
    except (TypeError,ValueError): return jsonify(error="f_hz et D_gpc doivent être numériques"),400
    dphi=HW["ego"]["eps"]*(f/100)*distance
    return jsonify(module="Ligo-Box V1.2",version="10.8",mode=HW["mode"],parametres={"Tr_T":HW["ego"]["Tr_T"],"RC_RO":HW["ligo"]["imu"],"epsilon":HW["ttd"]["eps"],"delta_phi_rad":dphi,"doi":HW["ttd"]["doi"]},hardware={"egobox":HW["ego"],"ligobox":HW["ligo"]},timestamp=now())
@app.route("/api/hardware/pilot",methods=["GET","POST"])
def pilot():
    simulate()
    data=request.get_json(silent=True) or request.args
    device=str(data.get("device","egobox")); command=str(data.get("command","read_all"))
    if device not in {"egobox","ligobox"}: return jsonify(error="device doit être egobox ou ligobox"),400
    if command not in {"read_all","led_on","led_off","ssr_on","ssr_off"}: return jsonify(error="Commande inconnue"),400
    if device=="egobox" and command in {"led_on","led_off"}: HW["ego"]["led"]=(command=="led_on")
    elif device=="ligobox" and command in {"ssr_on","ssr_off"}: HW["ligo"]["ssr"]=(command=="ssr_on")
    else: command="read_all"
    log_event("COMMANDE_DEMO",f"{device}:{command}")
    return jsonify(ok=True,mode=HW["mode"],hardware="SIMULATED",ego=HW["ego"],ligo=HW["ligo"],timestamp=now())
@app.route("/api/sector/<sid>",methods=["GET","POST"])
def sector(sid):
    if sid not in SECTEURS: return jsonify(error="Secteur inconnu",sectors=list(SECTEURS)),404
    simulate(); payload=request.get_json(silent=True) or {}
    action=str(payload.get("action","read_all"))
    if request.method=="POST":
        if action not in {"read_all","led_on","led_off","ssr_on","ssr_off"}: return jsonify(error="Action inconnue"),400
        if action in {"led_on","led_off"}: HW["ego"]["led"]=(action=="led_on")
        if action in {"ssr_on","ssr_off"}: HW["ligo"]["ssr"]=(action=="ssr_on")
        with db() as con: con.execute("INSERT INTO telemetry(secteur,Tr_T,RC_RO,delta_phi,payload,ts) VALUES(?,?,?,?,?,?)",(sid,HW["ego"]["Tr_T"],HW["ligo"]["imu"],HW["ttd"]["eps"],json.dumps(payload,ensure_ascii=False),now()))
        log_event("SECTEUR",f"{sid}:{action}")
    return jsonify(ok=True,sector=sid,nom=SECTEURS[sid]["nom"],mode=HW["mode"],hardware="SIMULATED",hw=HW["ego"],ligo=HW["ligo"],timestamp=now())
@app.post("/api/ask")
def ask():
    simulate(); data=request.get_json(silent=True) or {}; question=str(data.get("question","État général"))[:500]
    try: f=max(0.0,min(float(data.get("f_hz",1000)),1e9)); distance=max(0.0,min(float(data.get("D_gpc",1)),1e6))
    except (TypeError,ValueError): return jsonify(error="f_hz et D_gpc doivent être numériques"),400
    dphi=HW["ttd"]["eps"]*(f/100)*distance
    answer=f"Oracle TTD (mode {HW['mode']}) — Question : {question}. Température simulée : {HW['ego']['T']} °C ; Tr(T) simulé : {HW['ego']['Tr_T']} ; IMU simulée : {HW['ligo']['imu']} ; Δφ calculé selon le modèle configuré : {dphi:.3e} rad. I_TTD affiché : {HW['ttd']['I']:.3f}. Ces valeurs ne constituent pas une validation scientifique ni une mesure physique."
    log_event("ORACLE_QUESTION",question)
    return jsonify(answer=answer,delta_phi=dphi,mode=HW["mode"],hardware="SIMULATED",timestamp=now())
@app.get("/api/telemetry")
def telemetry():
    limit=request.args.get("limit",50,type=int); limit=max(1,min(limit or 50,200))
    with db() as con: data=[dict(r) for r in con.execute("SELECT * FROM telemetry ORDER BY id DESC LIMIT ?",(limit,)).fetchall()]
    return jsonify(data)
@app.get("/api/events")
def events():
    with db() as con: data=[dict(r) for r in con.execute("SELECT * FROM events ORDER BY id DESC LIMIT 100").fetchall()]
    return jsonify(data)
@app.errorhandler(500)
def server_error(exc):
    app.logger.exception("Erreur serveur",exc_info=exc)
    return jsonify(error="Erreur interne. Consultez les journaux serveur."),500
init_db()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT","10000")),debug=False)
