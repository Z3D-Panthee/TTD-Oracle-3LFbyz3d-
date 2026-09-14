from flask import Flask, render_template, send_from_directory, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('templates', 'manifest.json')

@app.route('/service-worker.js')
def sw():
    return send_from_directory('templates', 'service-worker.js', mimetype='application/javascript')

@app.route('/icon-192.png.jpg')
def icon192():
    return send_from_directory('templates', 'icon-192.png.jpg')

@app.route('/icon-512.png.jpg')
def icon512():
    return send_from_directory('templates', 'icon-512.png.jpg')

@app.route('/icon-1024.png.jpg')
def icon1024():
    return send_from_directory('templates', 'icon-1024.png.jpg')

@app.route('/api/ask', methods=['POST'])
def ask_api():
    data = request.get_json() or {}
    q = data.get('question','')
    return jsonify({
        "answer": f"TTD ORACLE v4.1.2 Lemba — Reçu: {q}",
        "k": 0.89, "ds": 0.32, "confidence": 0.87, "domain": "général"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))