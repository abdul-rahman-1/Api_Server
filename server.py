from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv('.env')

app = Flask(__name__)

# ✅ Allow full CORS access from anywhere
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Environment variables
PORT = int(os.getenv("PORT", 3000))
SERV = os.getenv("SERV")
MONGODB_URL = os.getenv("MONGODB_URL")

print(f"[STARTUP] SERVER_KEY={SERV[:6]}... | MONGO_URL={MONGODB_URL[:20]}... | PORT={PORT}")

# --------------------- Helpers ---------------------

def get_mongo_client():
    """Return MongoDB client connection."""
    return MongoClient(MONGODB_URL)

def check_auth():
    """Validate API key from 'serv' header."""
    provided_key = request.headers.get("serv")
    if provided_key != SERV:
        print(f"[AUTH] Invalid key attempt: {provided_key}")
        return False
    return True

# --------------------- Routes ---------------------

@app.route('/')
def home():
    """Redirect root to main frontend."""
    return redirect("https://rk-iot.netlify.app/", code=302)


@app.route('/api/Store', methods=['GET'])
def get_store():
    """Return all product data from MongoDB."""
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with get_mongo_client() as client:
            db = client["Store"]
            products = list(db["Products"].find({}))
            for p in products:
                p["_id"] = str(p["_id"])
            return jsonify(products)
    except Exception as e:
        print(f"[ERROR:/api/Store] {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/api/data', methods=['GET', 'OPTIONS'])
def get_data():
    """Return sensor data from MongoDB."""
    if request.method == "OPTIONS":
        return jsonify({"message": "CORS preflight OK"}), 200

    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with get_mongo_client() as client:
            db = client["Sensor"]
            sensor_data = list(db["Data"].find({}))
            for d in sensor_data:
                d["_id"] = str(d["_id"])
            print(f"[DATA] Returned {len(sensor_data)} records")
            return jsonify(sensor_data)
    except Exception as e:
        print(f"[ERROR:/api/data] {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }), 200


@app.route('/cron', methods=['GET'])
def cron_job():
    """
    Optional endpoint for cron pings or background tasks.
    Example: used by UptimeRobot or Render cron job.
    """
    try:
        # Example job: check MongoDB connection
        with get_mongo_client() as client:
            db_list = client.list_database_names()
        print(f"[CRON] Ping successful at {datetime.now()}, DBs: {db_list}")
        return jsonify({
            "cron": "executed",
            "databases": db_list,
            "time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }), 200
    except Exception as e:
        print(f"[CRON ERROR] {e}")
        return jsonify({"error": str(e)}), 500

# --------------------- Entry Point ---------------------

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT, debug=True)
