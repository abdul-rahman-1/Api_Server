from flask import Flask, jsonify, request, redirect
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)

PORT = int(os.getenv("PORT", 3000))
SERV = os.getenv("SERV")
MONGODB_URL = os.getenv("MONGODB_URL")

print(f"{SERV}||{MONGODB_URL}||{PORT}||")

def get_mongo_client():
    return MongoClient(MONGODB_URL)

def check_auth():
    provided_key = request.headers.get("serv")
    if provided_key != SERV:
        return False
    return True

@app.route('/')
def home():
    return jsonify({"Dara on": "/Data Rout"}), 200
    
@app.route('/data', methods=['GET'])
def redirect_data():
    return redirect("https://www.youtube.com/shorts/HpsREFRAXFQ", code=302)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

# ---------------------- SENSOR DATA ----------------------
@app.route('/api/data', methods=['GET'])
def get_data():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        client = get_mongo_client()
        db = client["Sensor"]
        sensor_data = list(db["Data"].find({}))
        for d in sensor_data:
            d["_id"] = str(d["_id"])
        return jsonify(sensor_data)
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        client.close()

# ---------------------- PLANT DATA ----------------------
@app.route('/api/plant/<int:plant_id>', methods=['GET'])
def get_plant(plant_id):
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        if plant_id < 1 or plant_id > 5:
            return jsonify({"error": "Invalid plant ID. Must be between 1 and 5."}), 400

        client = get_mongo_client()
        db = client["Sensor"]
        collection_name = f"Plant_{plant_id}"

        plant_data = list(db[collection_name].find({}))
        for p in plant_data:
            p["_id"] = str(p["_id"])

        return jsonify(plant_data)
    except Exception as e:
        print(f"Error fetching {collection_name}: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        client.close()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
