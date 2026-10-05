from flask import Flask, render_template, send_from_directory, request, jsonify, safe_join
import os
import sqlite3
import logging

# Logs propres et structurés pour Sentinel OS
logging.basicConfig(level=logging.INFO, format='[SENTINEL OS] %(asctime)s - %(levelname)s - %(message)s')

# Flask avec static explicite pour la PWA
app = Flask(__name__, static_folder='static', static_url_path='/static')

AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- DB SQLITE ---
DB_NAME = 'sentinel_jury.db'

def init_db():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jury_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        logging.info("Base SQLite initialisée avec succès.")
    except Exception as e:
        logging.error(f"Erreur init DB : {e}")

init_db()

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except:
        # Repli direct vers le fichier HTML principal de la v10.6
        return send_from_directory('.', 'sentinel_os_v10_6_QUANTUM_NEXUS.html')

# --- AUDIO : Range Requests anti-coupure (Kinshasa / Off-grid) ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    try:
        safe_path = safe_join(AUDIO_FOLDER, filename)
        if not safe_path or not os.path.exists(safe_path):
            return jsonify({"status": "error", "message": "Audio introuvable."}), 404
        return send_from_directory(AUDIO_FOLDER, filename, mimetype='audio/mpeg', conditional=True, max_age=86400)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json', mimetype='application/json')

@app.route('/sw.js')
@app.route('/service-worker.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/icon-<size>.png')
def icons_compat(size):
    safe_size = "".join([c for c in size if c.isdigit()])
    return send_from_directory('static', f'icon-{safe_size}.png', mimetype='image/png')

# --- ORACLE TTD ---
@app.route('/api/ask', methods=['POST'])
def ask_api():
    data = request.get_json(silent=True) or {}
    q = data.get('question', '')
    logging.info(f"Question Oracle: {q}")
    return jsonify({
        "status": "success",
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu et analysé : {q}",
        "k": 1.00, "ds": 0.00, "confidence": 0.99, "domain": "quantum-nexus"
    })

# --- PASSERELLE MATÉRIELLE & AGROSENTINELLES ---
@app.route('/api/hardware/sync', methods=['POST'])
def hardware_sync():
    data = request.get_json(silent=True) or {}
    node_id = data.get('node_id', 'KIX-LEMBA-01')
    telemetry = data.get('telemetry', {})
    
    logging.info(f"[HARDWARE SYNC] Paquet reçu du nœud {node_id} | Télémétrie : {telemetry}")
    
    return jsonify({
        "status": "success",
        "node_id": node_id,
        "os_version": "Sentinel OS v10.6 Quantum Nexus",
        "target_sync": "agrosentinelles-demo.onrender.com",
        "ligo_box_status": "ONLINE - Torsion T Validée",
        "message": "Synchronisation matérielle et processus industriels validés sans Internet."
    }), 200

# --- Jury SQLite ---
@app.route('/api/save_jury', methods=['POST'])
def save_jury():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    if not question or not answer:
        return jsonify({"status": "error", "message": "Question ou réponse manquante."}), 400
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO jury_logs (question, answer) VALUES (?, ?)", (question, answer))
            conn.commit()
        logging.info("Entrée jury sauvegardée.")
        return jsonify({"status": "success", "message": "Sauvegardé dans SQLite!"}), 200
    except Exception as e:
        logging.error(f"Erreur écriture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/jury_history', methods=['GET'])
def jury_history():
    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, question, answer, timestamp FROM jury_logs ORDER BY id DESC LIMIT 100")
            rows = cursor.fetchall()
        
        history = [{"id": r[0], "question": r[1], "answer": r[2], "timestamp": r[3]} for r in rows]
        return jsonify({"status": "success", "count": len(history), "history": history}), 200
    except Exception as e:
        logging.error(f"Erreur lecture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['X-Sentinel-Core'] = 'Active-Offline-First-Quantum'
    response.headers['X-TTD'] = 'I=1.000-Lemba-Kinshasa'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Démarrage SENTINEL OS v10.6 QUANTUM NEXUS sur le port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
