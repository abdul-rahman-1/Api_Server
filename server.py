from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

PORT = int(os.getenv("PORT", 3000))
SERV = os.getenv("SERV")
MONGODB_URL = os.getenv("MONGODB_URL")


def get_mongo_client():
    return MongoClient(MONGODB_URL)


def check_auth():
    provided_key = request.headers.get("serv")
    return provided_key == SERV


# --------------------------------------------------
# ROOT ROUTE — MESSAGE + AUTO REDIRECT AFTER 5 SEC
# --------------------------------------------------
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>LeafLens API</title>

        <!-- Bootstrap 5 -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

        <meta http-equiv="refresh" content="5;url=https://rk-iot.netlify.app/">
    </head>
    <body class="bg-dark text-light d-flex align-items-center justify-content-center vh-100">

        <div class="card bg-secondary text-light shadow-lg p-4 text-center" style="max-width: 600px;">
            <h2 class="mb-3">LeafLens Backend API</h2>
            <p>This server powers the LeafLens IoT & AI monitoring system.</p>
            <p class="fw-bold text-warning">
                Redirecting to the dashboard in 5 seconds…
            </p>
            <a href="/data" class="btn btn-warning mt-3">
                See our data, hack our data, or access the dashboard — go to the data route
            </a>

            <p class="mt-2">
                <a href="/data" class="text-info text-decoration-underline">
                    See Our Data
                </a>
            </p>
            <a href="https://rk-iot.netlify.app/" class="btn btn-info mt-3">
                Go Now
            </a>
        </div>

    </body>
    </html>
    """, 200


# --------------------------------------------------
# DATA ROUTE — TROLL + YOUTUBE IFRAME (NO REDIRECT)
# --------------------------------------------------
@app.route('/data', methods=['GET'])
def data_page():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>No Data Here</title>

        <!-- Bootstrap 5 -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-black text-light">

        <div class="container py-5">
            <div class="row justify-content-center">
                <div class="col-lg-8 text-center">

                    <div class="card bg-dark text-light shadow-lg p-4">
                        <h2 class="mb-3">Nice try 👀</h2>

                        <p class="lead">
                            You won’t find sensor data on this route.
                        </p>

                        <p>
                            To view real-time IoT data, AI plant analysis, and dashboards,
                            visit:
                        </p>

                        <a href="https://rk-iot.netlify.app/"
                           target="_blank"
                           class="btn btn-success mb-4">
                            LeafLens Dashboard
                        </a>

                        <hr class="border-secondary">

                        <p class="text-warning fw-bold">
                            Until then, enjoy this masterpiece:
                        </p>

                        <div class="ratio ratio-16x9 mt-3 d-none" id="videoBox">
                            <iframe
                                id="yt"
                                src="https://www.youtube.com/embed/HpsREFRAXFQ?autoplay=1"
                                allow="autoplay; encrypted-media"
                                allowfullscreen>
                            </iframe>
                        </div>

                        <p class="mt-4 text-muted">
                            API routes are protected. Curiosity is appreciated.
                        </p>
                    </div>

                </div>
            </div>
        </div>

    </body>
    </html>
    """, 200


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200


# --------------------------------------------------
# SENSOR DATA API (PROTECTED)
# --------------------------------------------------
@app.route('/api/data', methods=['GET'])
def get_data():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        client = get_mongo_client()
        db = client["Sensor"]
        data = list(db["Data"].find({}))

        for d in data:
            d["_id"] = str(d["_id"])

        return jsonify(data), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        client.close()


# --------------------------------------------------
# PLANT DATA API (PROTECTED)
# --------------------------------------------------
@app.route('/api/plant/<int:plant_id>', methods=['GET'])
def get_plant(plant_id):
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    if plant_id < 1 or plant_id > 5:
        return jsonify({"error": "Invalid plant ID (1–5 only)"}), 400

    try:
        client = get_mongo_client()
        db = client["Sensor"]
        collection = f"Plant_{plant_id}"

        plant_data = list(db[collection].find({}))
        for p in plant_data:
            p["_id"] = str(p["_id"])

        return jsonify(plant_data), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        client.close()


# --------------------------------------------------
# LOCAL RUN (Gunicorn for production)
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)
