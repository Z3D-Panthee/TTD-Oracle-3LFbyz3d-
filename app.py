from flask import Flask, render_template, send_from_directory, request, jsonify
import os

app = Flask(__name__)

# Dossier audio
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

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

# Les icônes sont servies auto par Flask depuis /static/
# Mais on garde une compatibilité si index.html appelle /icon-192.png
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

@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))