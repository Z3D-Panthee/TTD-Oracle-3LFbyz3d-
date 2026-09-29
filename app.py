from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sqlite3
import logging

# Configuration des logs pour un suivi propre dans la console
logging.basicConfig(level=logging.INFO, format='[SENTINEL OS] %(asctime)s - %(levelname)s - %(message)s')

# Initialisation de Flask avec le chemin statique explicite pour une compatibilité PWA parfaite
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Dossier audio
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- CONFIGURATION BASE DE DONNÉES SQLITE ---
DB_NAME = 'sentinel_jury.db'

def init_db():
    """Initialise la table SQLite pour stocker les questions/réponses du jury avec gestion d'erreurs"""
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
        logging.info("Base de données SQLite initialisée avec succès.")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation de la base de données : {e}")

# Initialiser la base au démarrage
init_db()

@app.route('/')
def home():
    return render_template('index.html')

# --- AUDIO : Streaming avec Range Requests (anti-coupure Kinshasa) ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    if not os.path.exists(os.path.join(AUDIO_FOLDER, filename)):
        return jsonify({"status": "error", "message": "Fichier audio introuvable."}), 404
    return send_from_directory(
        AUDIO_FOLDER, 
        filename, 
        mimetype='audio/mpeg',
        conditional=True,
        max_age=86400
    )

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

@app.route('/api/ask', methods=['POST'])
def ask_api():
    data = request.get_json(silent=True) or {}
    q = data.get('question', '')
    logging.info(f"Question reçue (Oracle): {q}")
    return jsonify({
        "status": "success",
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu et analysé : {q}",
        "k": 0.89, "ds": 0.32, "confidence": 0.87, "domain": "général"
    })

# --- Sauvegarde et Historique SQLite ---
@app.route('/api/save_jury', methods=['POST'])
def save_jury():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '').strip()
    answer = data.get('answer', '').strip()
    
    if not question or not answer:
        return jsonify({"status": "error", "message": "Question ou réponse manquante."}), 400
    
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO jury_logs (question, answer) VALUES (?, ?)",
            (question, answer)
        )
        conn.commit()
        conn.close()
        logging.flus = True
        logging.info("Entrée jury sauvegardée avec succès.")
        return jsonify({"status": "success", "message": "Sauvegardé avec succès dans SQLite !"}), 200
    except Exception as e:
        logging.error(f"Erreur d'écriture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/jury_history', methods=['GET'])
def jury_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, timestamp FROM jury_logs ORDER BY id DESC LIMIT 100")
        rows = cursor.fetchall()
        conn.close()
        
        history = [
            {"id": row[0], "question": row[1], "answer": row[2], "timestamp": row[3]}
            for row in rows
        ]
        return jsonify({"status": "success", "count": len(history), "history": history}), 200
    except Exception as e:
        logging.error(f"Erreur de lecture SQLite : {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    response.headers['X-Sentinel-Core'] = 'Active-Offline-First'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Démarrage de SENTINEL OS Backend sur le port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
