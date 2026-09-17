from flask import Flask, render_template, send_from_directory, request, jsonify
import os
import sqlite3

app = Flask(__name__)

# Dossier audio
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- CONFIGURATION BASE DE DONNÉES SQLITE ---
DB_NAME = 'sentinel_jury.db'

def init_db():
    """Initialise la table SQLite pour stocker les questions/réponses du jury"""
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

# Initialiser la base au démarrage
init_db()

@app.route('/')
def home():
    return render_template('index.html')

# --- AUDIO : Streaming avec Range Requests (anti-coupure Kinshasa) ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
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
    data = request.get_json() or {}
    q = data.get('question','')
    return jsonify({
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu: {q}",
        "k": 0.89, "ds": 0.32, "confidence": 0.87, "domain": "général"
    })

# --- NOUVELLES ROUTES : Sauvegarde et Historique SQLite ---
@app.route('/api/save_jury', methods=['POST'])
def save_jury():
    data = request.get_json() or {}
    question = data.get('question', '')
    answer = data.get('answer', '')
    
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
        return jsonify({"status": "success", "message": "Sauvegardé avec succès dans SQLite !"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/jury_history', methods=['GET'])
def jury_history():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, question, answer, timestamp FROM jury_logs ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        history = [
            {"id": row[0], "question": row[1], "answer": row[2], "timestamp": row[3]}
            for row in rows
        ]
        return jsonify({"status": "success", "history": history}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
