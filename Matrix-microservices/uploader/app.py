from flask import Flask, request, jsonify
import requests
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
SPLITTER_URL = "http://splitter:5001/split"

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    A = data["A"]
    B = data["B"]
    tile_r = data.get("tile_r", 2)
    tile_c = data.get("tile_c", 2)

    logging.info("Submitting matrices to splitter")
    requests.post(SPLITTER_URL, json={"A": A, "B": B, "tile_r": tile_r, "tile_c": tile_c})
    return jsonify({"status":"started"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
