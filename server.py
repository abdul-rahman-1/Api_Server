from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv('.env')

app = Flask(__name__)
CORS(app)

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
    return redirect("https://rk-iot.netlify.app/", code=302)

@app.route('/api/Store', methods=['GET'])
def get_store():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        client = get_mongo_client()
        db = client["Store"]
        products = list(db["Products"].find({}))
        # convert Mongo ObjectId to str for JSON serialization
        for p in products:
            p["_id"] = str(p["_id"])
        return jsonify(products)
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal Server Error"}), 500
    finally:
        client.close()

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=PORT)
