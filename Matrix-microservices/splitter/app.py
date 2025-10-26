from flask import Flask, request, jsonify
import requests
import numpy as np
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKERS = ["http://worker1:5002/compute",
           "http://worker2:5002/compute",
           "http://worker3:5002/compute"]
AGGREGATOR_URL = "http://aggregator:5003/aggregate"

app = Flask(__name__)

# Global progress tracking
PROGRESS = {"current": 0, "total": 0, "percentage": 0, "status": "idle"}

def process_matrices(A, B, tile_r, tile_c):
    global PROGRESS
    
    brA, bcA = A.shape[0] // tile_r, A.shape[1] // tile_c
    brB, bcB = B.shape[0] // tile_r, B.shape[1] // tile_c

    logger.info(f"Splitting matrices of size {A.shape} x {B.shape} into tiles {tile_r}x{tile_c}")

    # Calculate total operations
    total_ops = brA * bcB * bcA
    PROGRESS = {"current": 0, "total": total_ops, "percentage": 0, "status": "processing"}

    # Split matrices into blocks
    A_blocks = {(i,j): A[i*tile_r:(i+1)*tile_r, j*tile_c:(j+1)*tile_c] for i in range(brA) for j in range(bcA)}
    B_blocks = {(i,j): B[i*tile_r:(i+1)*tile_r, j*tile_c:(j+1)*tile_c] for i in range(brB) for j in range(bcB)}

    # Send to workers
    widx = 0
    C_blocks = {}
    for i in range(brA):
        for j in range(bcB):
            C_accum = None
            for k in range(bcA):
                payload = {
                    "A_block": A_blocks[(i,k)].tolist(),
                    "B_block": B_blocks[(k,j)].tolist()
                }
                logger.info(f"Sending block ({i},{k}) x ({k},{j}) to worker {widx % len(WORKERS)}")
                resp = requests.post(WORKERS[widx % len(WORKERS)], json=payload)
                partial = np.array(resp.json()["C_block"])
                if C_accum is None:
                    C_accum = partial
                else:
                    C_accum += partial
                widx += 1
                
                # Update progress
                PROGRESS["current"] += 1
                PROGRESS["percentage"] = int((PROGRESS["current"] / PROGRESS["total"]) * 100)
                logger.info(f"Progress: {PROGRESS['percentage']}%")
                
            # Convert tuple key to string for JSON
            C_blocks[f"{i},{j}"] = C_accum.tolist()

    logger.info("Sending computed blocks to aggregator")
    requests.post(AGGREGATOR_URL, json={"C_blocks": C_blocks, "tile_r": tile_r, "tile_c": tile_c})
    
    # Mark as complete
    PROGRESS = {"current": total_ops, "total": total_ops, "percentage": 100, "status": "complete"}

@app.route("/split", methods=["POST"])
def split_matrices():
    global PROGRESS
    data = request.get_json()
    A = np.array(data["A"])
    B = np.array(data["B"])
    tile_r = data["tile_r"]
    tile_c = data["tile_c"]

    # Reset progress
    PROGRESS = {"current": 0, "total": 0, "percentage": 0, "status": "starting"}
    
    # Process in background thread
    thread = threading.Thread(target=process_matrices, args=(A, B, tile_r, tile_c))
    thread.start()
    
    return jsonify({"status": "started"})

@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(PROGRESS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)