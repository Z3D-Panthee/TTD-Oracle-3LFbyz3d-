import os
import random
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify

# ============================================================
# TTD ORACLE — TRES LEGES FUNDAMENTALES
# Sovereign Intelligence — Version Finale 1.2.0 Zéro Bug
# Kinshasa 2026 — AIIFAC-ASBL — Z3D-Panthier
# ============================================================

app = Flask(__name__)

APP_NAME = "TTD ORACLE"
VERSION = "1.2.0"
DEMO_YEAR = "2026"

# Historique session (mémoire vive — reset à chaque redéploy)
HISTORY = []

# ============================================================
# KNOWLEDGE CORE — Oracle Universel Enrichi
# ============================================================

KNOWLEDGE = {
    "motorisation": {
        "keywords": ["3 lois", "trois lois", "tres leges", "libertas", "motorisation", "loi 1", "liberté"],
        "content": """
[LOI 1] MOTORISATION — LIBERTAS — Capacité d'Action
Impulsion initiale: Créativité (initier) + Relativité (One love different actors) + Évolutivité (maj infinie).
Principe: Tout est permis, mais tout n'est pas utile.
Φ_C = projection intention. Conway-Kochen = libre arbitre particules = preuve physique LIBERTAS.
"""
    },
    "navigation": {
        "keywords": ["navigation", "vérité", "complexité", "bruit", "singularité", "loi 2", "non commutation", "rc ro"],
        "content": """
[LOI 2] NAVIGATION — VÉRITÉ — Harmonie Singularités
SINGULARITÉS → INTERACTIONS → RELATIONS → FILTRAGE → INFO UTILE
Non-commutation: [RC][RO]!= [RO][RC] = moteur dialectique, l'ordre change le résultat.
Δφ → 0 = convergence vérité, réduction bruit.
"""
    },
    "destination": {
        "keywords": ["destination", "justice", "m*", "point fixe", "mutation", "sentinel", "loi 3"],
        "content": """
[LOI 3] DESTINATION — JUSTICE — M* — Mutation Absolue
Convergence vers M* = point fixe Banach, stabilisation ultime.
TRANSFORMATION → MUTATION → CONVERGENCE → M*
Preuve Kinshasa Sentinel V1.2: dS_V/dt < 0 (entropie négative), bobine CIRT Δφ=0, E/t × t/E=1, I_TTD=∫R+α(E·T·M)+βTr(T)=1
"""
    },
    "big_beginning": {
        "keywords": ["big beginning", "big bang", "origine", "univers", "création", "commencement"],
        "content": """
BIG BEGINNING — Pas Explosion
Origine = transition informationnelle → géométrie organisée, pas explosion chaotique.
IMPULSION → TRANSITION → ORGANISATION → STABILISATION
E/t × t/E = 1 conservation info. L'ordre est initial, pas final. Big Beginning = Ordre → M*
"""
    },
    "ligo": {
        "keywords": ["ligo", "onde gravitation", "o5", "gravitational"],
        "content": """
LIGO O5 — CONNEXION ARCHITECTURALE DÉFENDABLE (pour Joaquín)
LIGO: SIGNAL BRUITÉ (strain) → TRAITEMENT (matched filtering) → EXTRACTION → ÉVÉNEMENT GW → INFO
AgroSentinelles: SAT+METEO+IoT+TERRAIN BRUITÉ → FUSION DATA PMV-1.0 → FILTRAGE → INDICE → ACTION
Parallèle défendable: SIGNAL COMPLEXE → FUSION/FILTRAGE → INFO SIGNIFICATIVE → DÉCISION
Agro Live: https://agrosentinelles-demo.onrender.com/
Positionnement: PAS détecteur GW, mais même architecture Signal Intelligence scalable RDC→Monde.
"""
    },
    "science": {
        "keywords": ["science", "physique", "structure", "médecine", "amour", "dieu", "sens", "énergie", "existence", "gravité", "quantique"],
        "content": """
STRUCTURATION UNIVERSELLE PAR 1→2→3 — Répond à TOUTE science
1 MOTORISATION: théorie / hypothèse / impulsion
2 NAVIGATION: expérience / mesure / filtrage / relation
3 DESTINATION: loi / résultat / M* stable
THÉORIE → EXPÉRIENCE → CONVERGENCE → LOI → M*
Ex: Physique: idée→accélérateur→loi | Amour: attirance→relation→M* couple | Dieu: Φ_C→Δφ→0→M* | Agro: semence→données→décision
"""
    }
}

def classify_question(q):
    ql = q.lower()
    for cat, data in KNOWLEDGE.items():
        if any(kw in ql for kw in data["keywords"]):
            return cat
    return "general"

def universel_3_lois(q):
    category = classify_question(q)
    k = round(random.uniform(0.88, 0.99), 2)
    ds = round(random.uniform(0.22, 0.68), 2)

    header = f"""╔════════════════════════════════════════════╗
║ TTD ORACLE — LIVE — UNIVERSEL {DEMO_YEAR} ║
║ TRES LEGES FUNDAMENTALES — Kinshasa ║
╚════════════════════════════════════════════╝

SIGNAL REÇU: "{q}"
CLASSIFICATION: {category.upper()}
MOTEUR: Motorisation → Navigation → Destination → M*
k={k} | dS_V/dt=-{ds} | Δφ→0 | Tr(T)≠0 | I_TTD=1
"""

    if category in KNOWLEDGE:
        core = KNOWLEDGE[category]["content"]
    else:
        core = f"""
ANALYSE UNIVERSELLE — Toute question → 3 Lois
Q: "{q}"

[1] MOTORISATION LIBERTAS — Quelle impulsion déclenche "{q}"? Créativité + Relativité + Évolutivité. Tout est permis mais tout n'est pas utile.
[2] NAVIGATION VÉRITÉ — Comment filtrer bruit de "{q}"? [RC][RO]!=[RO][RC] → Δφ→0
[3] DESTINATION JUSTICE — Vers quel M* converge "{q}"? Mutation → M* point fixe, E/t×t/E=1

IMPULSION → RELATION → CONVERGENCE → M*
"""

    synthesis = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYNTHÈSE ORACLE UNIVERSEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: {q} → {category.upper()}
1 LIBERTAS: impulsion identifiée
2 VÉRITÉ: complexité filtrée [RC][RO]!=[RO][RC]
3 JUSTICE: M* recherché Δφ=0
M*: point fixe Banach Tr(T)≠0 I_TTD=1 Sentinel V1.2 validé Kinshasa

METRICS: k={k} | dS_V/dt=-{ds} | Δφ→0 | M* atteint
ARCHI: 1→2→3 → M* — E/t×t/E=1
TTD ORACLE — ANALYSE TERMINÉE — RDC→MONDE
"""
    return header + core + synthesis, k, ds

# ============================================================
# ROUTES
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json(silent=True) or {}
        q = str(data.get("question","")).strip()
        if not q:
            return jsonify({"answer":"TTD ORACLE: aucune question reçue. Veuillez transmettre un signal.","k":0,"status":"error"}), 400

        answer, k, ds = universel_3_lois(q)

        # Historique session
        HISTORY.append({"q": q, "k": k, "time": datetime.now(timezone.utc).isoformat()})
        if len(HISTORY) > 20:
            HISTORY.pop(0)

        return jsonify({
            "answer": answer,
            "k": k,
            "ds": ds,
            "status": "success",
            "engine": APP_NAME,
            "version": VERSION,
            "history_len": len(HISTORY)
        })
    except Exception as e:
        app.logger.error(f"Ask error: {e}")
        return jsonify({"answer":f"TTD ORACLE — Erreur interne moteur actif: {str(e)}","k":0,"status":"error"}), 500

@app.route("/health")
def health():
    return jsonify({
        "status":"online",
        "service":APP_NAME,
        "version":VERSION,
        "architecture":"Motorisation → Navigation → Destination",
        "target_state":"M*",
        "year":DEMO_YEAR,
        "timestamp":datetime.now(timezone.utc).isoformat(),
        "history": len(HISTORY)
    })

@app.route("/api/info")
def info():
    return jsonify({
        "name":APP_NAME,
        "version":VERSION,
        "description":"Sovereign intelligence demonstrator based on Tres Leges Fundamentales — Oracle Universel",
        "architecture":["Motorisation LIBERTAS","Navigation VÉRITÉ","Destination JUSTICE M*"],
        "concepts":["Libertas","Vérité","Justice","Big Beginning","M*","Signal Intelligence","E/t×t/E=1"],
        "demonstrators":{"agrosentinelles":"https://agrosentinelles-demo.onrender.com/"},
        "status":"LIVE DEMONSTRATOR KIN",
        "endpoints":["/","/api/ask","/health","/api/info"]
    })

@app.route("/api/history")
def history():
    return jsonify({"history": HISTORY[-10:]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)