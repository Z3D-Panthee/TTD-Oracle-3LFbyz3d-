"""QUANTUM NEXUS v11.0 — 3D PRO MAX — Flask FINAL — FrancoTech FREE"""
from datetime import datetime, timezone
from pathlib import Path
import logging, os, random, sqlite3
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("SENTINEL_DB_PATH", str(BASE_DIR / "quantum_nexus_jury.db")))
logging.basicConfig(level="INFO", format="[QN v11.0 3D] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["JSON_SORT_KEYS"] = False

# === 8 SECTEURS IRRÉFUTABLES — AVEC PERTES MOIS/AN + DEVIS + 70→98% ===
DOSSIER_8 = [
    {"id":"energy","nom":"Energy Sentinel","icone":"⚡","pertes_an":"1,2 Md$ / an","pertes_mois":"100 M$ / mois","source":"SNEL 600M$ Coupe Monde [DG SNEL] + Chambre Mines 1,5Md$ + BM 30% pertes","cause":"Fraude compteurs 60% non facturé, délestage non tracé","devis":"Smart Meter MPPT 342W 2300W x100 = 23 000$ | ESP32 Micro-CIRT + INA219 + DS18B20 + Relay 30A + LiFePO4 40Ah","gain70":"+840M$/an","gain98":"1,176Md$/an","b2g":"B2G 3% = 25,2M$ ROI x33","saas":"10$/mois particulier / 100$/mois PME"},
    {"id":"water","nom":"Water Sentinel","icone":"💧","pertes_an":"350M$ / an","pertes_mois":"29,1M$ / mois","source":"REGIDESO -45% Murhundu 31k→17k m³/j [bkinfos.cd 22 sept 2026]","cause":"Fuites 45% + forages non contrôlés 50L/h perdu","devis":"Distmeter + Vanne x05 1.000 = 2 000$ | YF-S201 1-100L/min + Vanne solénoïde 12V + ESP32","gain70":"+245M$/an","gain98":"343M$/an","b2g":"B2G 3% = 7,3M$","saas":"Paye à l'upload m³"},
    {"id":"pharma","nom":"Pharma Sentinel","icone":"🧪","pertes_an":"500M$ / an","pertes_mois":"41,6M$/mois","source":"OMS 35% contrefaçon Afrique","cause":"Contrefaçon 35% + ruptures stock + péremption","devis":"QR TTD + Sonde x05 1.000 = 4 000$ | DS18B20 frigo -40+85°C + QR Code TTD Blockchain locale","gain70":"+350M$/an","gain98":"490M$/an","b2g":"B2G 3% = 10,5M$","saas":"100$/mois pharmacie"},
    {"id":"mine","nom":"Mine Sentinel ★","icone":"⛏️","pertes_an":"4 Mds$ / an","pertes_mois":"333M$ / mois","source":"IGF 4,4Mds$ Perenco [congovirtuel 2026] + ARSP 20Mds$ sous-traitance + Cour comptes 16,8Mds$ + 1Md/an smuggling Rwanda","cause":"Sous-évaluation teneur + contrebande + non traçabilité + prête-noms","devis":"Balance + GPS 30G 50 = 15 000$ | HX711 50T + u-blox M10 + IA teneur + CEEC offline + SD 32GB","gain70":"+2,8Mds$/an","gain98":"3,92Mds$/an — Si 9Mds$/mois national = 108Mds$/an → 3,24Mds$ B2G","b2g":"B2G 3% = 84M$/an ROI x33","saas":"5000$/mois licence industrielle"},
    {"id":"security","nom":"Security Sentinel","icone":"🛡️","pertes_an":"200M$ / an","pertes_mois":"16,6M$/mois","source":"Cyber attaques CIRT","cause":"Cyberattaques + vols données + pannes CIRT","devis":"Boiter Micro-CIRT 120B x100 = 12 000$ | ARM Cortex-M4 120MHz + LoRaWAN + RTC","gain70":"+140M$/an","gain98":"196M$/an","b2g":"B2G 3% = 4,2M$","saas":"500$/mois SOC"},
    {"id":"logistics","nom":"Logistics Sentinel","icone":"🚚","pertes_an":"600M$ / an","pertes_mois":"50M$/mois","source":"40% camions vides + vol carburant","cause":"Camions vides 40% + carburant volé + retard","devis":"GPS + Jauge x100 = 9 000$ | u-blox M10 <2.5m + Jauge capacitive 0-100% + IMU 6DOF","gain70":"+420M$/an","gain98":"588M$/an","b2g":"B2G 3% = 12,6M$","saas":"100$/mois camion"},
    {"id":"brasserie","nom":"Brasserie Sentinel","icone":"🍺","pertes_an":"150M$ / an","pertes_mois":"12,5M$/mois","source":"Fermentation ratée + surstock","cause":"Variabilité fermentation + rebuts + surstock","devis":"Sonde pH 708 x100 = 7 000$ | pH 2-12 food-grade + T° inox 316","gain70":"+105M$/an ROI x87","gain98":"147M$/an","b2g":"B2G 3% = 3,15M$","saas":"100$/mois cuve"},
    {"id":"agro","nom":"Agro Sentinel","icone":"🌱","pertes_an":"1,5Md$ / an","pertes_mois":"125M$/mois","source":"FAO 50% récolte pourrie post-récolte","cause":"50% récolte pourrie + stress hydrique","devis":"Sonde NPK + Vanne 85B x100 = 8 000$ | N 0-1999ppm + P + K + Humidité + Drip","gain70":"+1,05Md$/an","gain98":"1,47Md$/an","b2g":"B2G 3% = 31,5M$","saas":"10$/mois hectare"},
]

SECTEURS = {d["id"]: {"nom": d["nom"], "icone": d["icone"]} for d in DOSSIER_8}

FRANCOTECH_APPS = {
    "true_north_rc": {"id":"true_north_rc","nom":"TRUE NORTH RC","subtitle":"Remote Control & Navigation","desc":"Monitoring temps réel","icone":"🧭","color":"#00eaff","version":"v11.0 3D FREE","hardware":"GPS 90$ + ESP32"},
    "supervpn_ro": {"id":"supervpn_ro","nom":"SUPERVPN RO","subtitle":"VPN Sécurisé RO","desc":"Connexion chiffrée AES-256","icone":"🔒","color":"#238cff","version":"v11.0 3D FREE","hardware":"AES-256-GCM"},
    "vault_ri": {"id":"vault_ri","nom":"VAULT RI","subtitle":"Coffre-fort Numérique RI","desc":"Stockage chiffré SQLite","icone":"🏦","color":"#ffd166","version":"v11.0 3D FREE","hardware":"SQLite chiffré"}
}

HW = {
    "mode":"DEMO 3D PRO MAX",
    "ego":{"T":26.3,"H":52.0,"Tr_T":0.0021,"eps":1e-5,"led":False,"gps":"-4.325°S 15.322°E LEMBA"},
    "ligo":{"imu":0.0042,"ssr":False,"mppt":28,"ip":"10.8.0.2"},
    "ttd":{"eps":1e-5,"doi":"10.5281/zenodo.19852087","I":1.000}
}

def now(): return datetime.now(timezone.utc).isoformat()
def get_db():
    con=sqlite3.connect(DB_PATH, timeout=20); con.row_factory=sqlite3.Row; return con
def init_db():
    try:
        with get_db() as con:
            con.execute("CREATE TABLE IF NOT EXISTS telemetry(id INTEGER PRIMARY KEY AUTOINCREMENT, secteur TEXT, Tr_T REAL, RC_RO REAL, delta_phi REAL, payload TEXT, ts TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT, details TEXT DEFAULT '', ts TEXT)")
            con.execute("CREATE TABLE IF NOT EXISTS vault_ri(id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT, encrypted INTEGER DEFAULT 1, size_kb INTEGER, ts TEXT)")
            cur=con.execute("SELECT COUNT(*) as c FROM vault_ri").fetchone()
            if cur["c"]==0:
                for f in [("rapport_snel_15nov.pdf",245),("gps_lemba_logs.enc",128),("francotech_inscription.json",12),("blueprint_energy_342W.png",2048),("blueprint_mine_HX711.png",2048)]:
                    con.execute("INSERT INTO vault_ri(filename,size_kb,ts) VALUES(?,?,?)",(f[0],f[1],now()))
            con.commit()
    except Exception as e: logger.error(f"DB init {e}")
def simulate():
    HW["ego"]["T"]=round(26+random.uniform(-0.5,0.8),1)
    HW["ego"]["Tr_T"]=round(0.0020+random.uniform(0,0.0005),5)
    HW["ligo"]["imu"]=round(0.004+random.uniform(-0.0005,0.001),5)
    HW["ego"]["gps"]=f"{-4.325+random.uniform(-0.01,0.01):.3f}°S {15.322+random.uniform(-0.01,0.01):.3f}°E LEMBA LIVE 3D"
    HW["ligo"]["ip"]=f"10.8.0.{random.randint(2,20)}"
init_db()

def find_and_serve(filename, mimetype=None):
    for d in [BASE_DIR, BASE_DIR/"templates", BASE_DIR/"static", BASE_DIR/"templates"/"static"]:
        fp=d/filename
        if fp.exists():
            return send_from_directory(d, filename, mimetype=mimetype) if mimetype else send_from_directory(d, filename)
    return None

@app.get("/")
def home():
    r=find_and_serve("index.html")
    return r if r else jsonify(status="QUANTUM NEXUS v11.0 3D PRO MAX online", searched=[str(BASE_DIR/"templates")])

@app.get("/manifest.json")
def manifest():
    r=find_and_serve("manifest.json", mimetype="application/manifest+json")
    return r if r else jsonify(name="QUANTUM NEXUS v11.0 3D", short_name="QN v11 3D")

@app.get("/sw.js")
@app.get("/service-worker.js")
def sw():
    for name in ["sw.js","service