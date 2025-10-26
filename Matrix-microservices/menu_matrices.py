import requests
import numpy as np
import time

UPLOADER_URL = "http://127.0.0.1:5000/submit"
AGGREGATOR_URL = "http://127.0.0.1:5003/result"
PROGRESS_URL = "http://127.0.0.1:5001/progress"

def main():
    print("=== Parallel Matrix Multiplication ===")
    n = int(input("Enter matrix size (n x n, max ~10 for testing): "))

    print("Generating two random matrices...")
    A = np.random.randint(0, 10, (n, n))
    B = np.random.randint(0, 10, (n, n))

    print("Matrix A:\n", A)
    print("Matrix B:\n", B)

    # Choose a tile size (for small n, tile=1)
    tile_r, tile_c = 100, 100
    payload = {"A": A.tolist(), "B": B.tolist(), "tile_r": tile_r, "tile_c": tile_c}

    print("Submitting matrices to uploader...")
    try:
        r = requests.post(UPLOADER_URL, json=payload)
        print("Submission successful:", r.json())
    except Exception as e:
        print("Failed to submit matrices:", e)
        return

    # Poll for progress and result
    print("\nProcessing matrices...")
    last_percentage = -1
    
    while True:
        try:
            # Check progress
            prog_resp = requests.get(PROGRESS_URL)
            if prog_resp.status_code == 200:
                progress = prog_resp.json()
                current_percentage = progress.get("percentage", 0)
                if current_percentage != last_percentage:
                    print(f"Progress: {current_percentage}% ({progress.get('current', 0)}/{progress.get('total', 0)} operations)", end="\r")
                    last_percentage = current_percentage
            
            # Check for result
            result_resp = requests.get(AGGREGATOR_URL)
            if result_resp.status_code == 200:
                data = result_resp.json()
                C = np.array(data["C"])
                print("\n\n=== Result Matrix C ===")
                print(C)
                break
                
        except Exception as e:
            print(f"\nError: {e}")
        
        time.sleep(0.1)

if __name__ == "__main__":

    main()
