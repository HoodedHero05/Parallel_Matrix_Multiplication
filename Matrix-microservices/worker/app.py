from flask import Flask, request, jsonify
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

@app.route("/compute", methods=["POST"])
def compute_block():
    data = request.get_json()
    A_block = np.array(data["A_block"])
    B_block = np.array(data["B_block"])
    logging.info("Received block for computation")

    C_block = A_block @ B_block  # matrix multiplication
    logging.info(f"Computed block:\n{C_block}")

    return jsonify({"C_block": C_block.tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
