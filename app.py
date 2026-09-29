from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sqlite3
import logging

# Logs propres
logging.basicConfig(level=logging.INFO, format='[SENTINEL OS] %(asctime)s - %(levelname)s - %(message)s')

# Flask avec static explicite pour PWA
app = Flask(__name__, static_folder='static', static_url_path='/static')

AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- DB SQLITE ---
DB_NAME = 'sentinel_jury.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
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
        conn.close()
        logging.info("Base SQLite initialisée.")
    except Exception as e:
        logging.error(f"Erreur init DB : {e}")

init_db()

@app.route('/')
def home():
    # Si tu as mis l'index dans templates/ -> render_template
    # Si tu as mis le fichier à la racine -> send_from_directory
    try:
        return render_template('index.html')
    except:
        return send_from_directory('.', 'sentinel_os_v10_QUANTUM_NEXUS_FINAL_8_SECTEURS.html')

# --- AUDIO : Range Requests anti-coupure Kinshasa ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    path = os.path.join(AUDIO_FOLDER, filename)
    if not os.path.exists(path):
        return jsonify({"status": "error", "message": "Audio introuvable."}), 404
    return send_from_directory(AUDIO_FOLDER, filename, mimetype='audio/mpeg', conditional=True, max_age=86400)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/service-worker.js')
def sw_alias():
    return send_from_directory('.', 'sw.js', mimetype='application/javascript')

@app.route('/icon-<size>.png')
def icons_compat(size):
    return send_from_directory('static', f'icon-{size}.png', mimetype='image/png')

# --- ORACLE TTD ---
@app.route('/api/ask', methods=['POST'])
def ask_api():
    data = request.get_json(silent=True) or {}
    q = data.get('question', '')
    logging.info(f"Question Oracle: {q}")
    return jsonify({
        "status": "success",
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu et analysé : {q}",
        "k": 0.89, "ds": 0.32, "confidence": 0.87, "domain": "général"
    })

# --- Jury SQLite ---
@app.route('/api/save_jury', methods=['POST'])
def save_jury():
    data = request.get_json(silent=True) or {}
    question = data.get('question','').strip()
    answer = data.get('answer','').strip()
    if not question or not answer:
        return jsonify({"status": "error", "message": "Question ou réponse manquante."}), 400
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO jury_logs (question, answer) VALUES (?,?)", (question, answer))
        conn.commit()
        conn.close()
        logging.info("Entrée jury sauvegardée.")
        return jsonify({"status": "success", "message": "Sauvegardé dans SQLite!"}), 200
    except Exception as e:
        logging.error(f"Erreur écriture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/jury_history', methods=['GET'])
def jury_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, timestamp FROM jury_logs ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        history = [{"id": r[0], "question": r[1], "answer": r[2], "timestamp": r[3]} for r in rows]
        return jsonify({"status": "success", "count": len(history), "history": history}), 200
    except Exception as e:
        logging.error(f"Erreur lecture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['X-Sentinel-Core'] = 'Active-Offline-First'
    response.headers['X-TTD'] = 'I=1.000-Lemba'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Démarrage SENTINEL OS v10 QUANTUM NEXUS FINAL 8 secteurs sur port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)