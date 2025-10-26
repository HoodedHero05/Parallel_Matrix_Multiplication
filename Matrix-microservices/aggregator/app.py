from flask import Flask, request, jsonify
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
FULL_MATRIX = None
TASK_DONE = False

@app.route("/aggregate", methods=["POST"])
def aggregate_blocks():
    global FULL_MATRIX, TASK_DONE
    data = request.get_json()
    C_blocks = data["C_blocks"]
    tile_r = data["tile_r"]
    tile_c = data["tile_c"]

    # Determine full matrix size from blocks
    max_i = max(int(k.split(",")[0]) for k in C_blocks.keys())
    max_j = max(int(k.split(",")[1]) for k in C_blocks.keys())
    FULL_MATRIX = np.zeros(((max_i+1)*tile_r, (max_j+1)*tile_c), dtype=int)

    # Place each block in the correct location
    for key, block in C_blocks.items():
        i, j = map(int, key.split(","))
        block = np.array(block)
        FULL_MATRIX[i*tile_r:(i+1)*tile_r, j*tile_c:(j+1)*tile_c] = block

    TASK_DONE = True
    logger.info(f"Aggregation complete. Full matrix size: {FULL_MATRIX.shape}")
    return jsonify({"status": "aggregated"})

@app.route("/result", methods=["GET"])
def get_result():
    global FULL_MATRIX, TASK_DONE
    if TASK_DONE and FULL_MATRIX is not None:
        result = {"C": FULL_MATRIX.tolist()}
        # Reset state after result is retrieved
        FULL_MATRIX = None
        TASK_DONE = False
        logger.info("Result retrieved, state reset for next job")
        return jsonify(result)
    else:
        return jsonify({"status": "processing"}), 202

@app.route("/reset", methods=["POST"])
def reset():
    global FULL_MATRIX, TASK_DONE
    FULL_MATRIX = None
    TASK_DONE = False
    logger.info("State manually reset")
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)