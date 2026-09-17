from flask import Flask, render_template, send_from_directory, request, jsonify, send_file
import os

app = Flask(__name__)
# Dossier où tu mettras tes mp3
AUDIO_FOLDER = os.path.join('static', 'audio')
os.makedirs(AUDIO_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# --- FIX AUDIO : Streaming avec Range Requests (anti-coupure) ---
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    # Support du streaming partiel (206 Partial Content)
    return send_from_directory(
        AUDIO_FOLDER, 
        filename, 
        mimetype='audio/mpeg',
        conditional=True,  # Active le 206
        max_age=86400
    )

@app.route('/manifest.json')
def manifest():
    return send_from_directory('templates', 'manifest.json')

@app.route('/service-worker.js')
def sw():
    return send_from_directory('templates', 'service-worker.js', mimetype='application/javascript')

# Corrige tes icons (enlève le .jpg double)
@app.route('/icon-<size>.png')
def icons(size):
    return send_from_directory('templates', f'icon-{size}.png.jpg')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    data = request.get_json() or {}
    q = data.get('question','')
    return jsonify({
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu: {q}",
        "k": 0.89, "ds": 0.32, "confidence": 0.87, "domain": "général"
    })

# Headers anti-coupure pour Kinshasa (cache + keep-alive)
@app.after_request
def after_request(response):
    response.headers['Accept-Ranges'] = 'bytes'
    response.headers['Cache-Control'] = 'public, max-age=86400'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))