from flask import Flask, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for the frontend

LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/packets.json')

@app.route('/api/packets', methods=['GET'])
def get_packets():
    if not os.path.exists(LOG_FILE):
        return jsonify([])
    
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    if not os.path.exists(LOG_FILE):
        return jsonify({})
    
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
            stats = {
                "total": len(data),
                "protocols": {}
            }
            for pkt in data:
                proto = pkt.get("protocol", "Unknown")
                stats["protocols"][proto] = stats["protocols"].get(proto, 0) + 1
            return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
