import time
import json
import random
import requests
from websocket import create_connection
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

BASE_WS_URL = "ws://<AWS_IP>"
BASE_URL = "http://<AWS_IP>"

WS_URL = f"{BASE_WS_URL}/ws/alert?id="
POST_URL = f"{BASE_URL}/test/fire-w-coords"
DELETE_URL = f"{BASE_URL}/test/fire"

ITERATIONS = 500
THREADS = 50

# Shared latency storage
push_latencies = []
total_latencies = []
latency_lock = Lock()

# Reusable location payload
location_payload = {
    "type": "update_location",
    "longitude": -121.875329832,
    "latitude": 37.334665328
}

fire_payload = {
    "latitude": 37.33466533,
    "longitude": -121.87532983
}

def run_single_test(test_id):
    """
    Runs ONE websocket test:
    1. Connect to WS
    2. Send location
    3. Sleep random delay (0-30s)
    4. POST fire inside BBOX
    5. Wait for websocket push
    6. Delete fire (cleanup)
    Returns (push_latency, total_latency)
    """

    ws_user_id = 1000 + test_id  # ensure unique WS ID per test

    try:
        # Connect WS
        ws = create_connection(f"{WS_URL}{ws_user_id}")

        # Send location
        push_start = time.time()
        ws.send(json.dumps(location_payload))
        push_end = time.time()

        push_latency_ms = (push_end - push_start) * 1000

        # Random delay simulating random fire arrival
        delay = random.uniform(0, 30)
        time.sleep(delay)

        # Measure full latency (POST -> ws.recv)
        total_start = time.time()
        post_res = requests.post(POST_URL, json=fire_payload)

        if post_res.status_code != 200:
            ws.close()
            return None, None

        fire_id = post_res.json().get("id")

        # Wait for WS notification
        ws_msg = ws.recv()
        total_end = time.time()

        total_latency_ms = (total_end - total_start) * 1000

        # Cleanup
        requests.delete(f"{DELETE_URL}/{fire_id}")
        ws.close()

        return push_latency_ms, total_latency_ms

    except Exception as e:
        print(f"[ERROR in test {test_id}] {e}")
        return None, None


# MAIN PARALLEL EXECUTION
def main():
    print(f"Running {ITERATIONS} tests with {THREADS} threads...\n")

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = [executor.submit(run_single_test, i) for i in range(ITERATIONS)]

        for f in as_completed(futures):
            push, total = f.result()
            if push is None:
                continue

            with latency_lock:
                push_latencies.append(push)
                total_latencies.append(total)

    print("\n--- RESULTS ---")

    print("\nWS Push Latency:")
    print(f"Average: {sum(push_latencies)/len(push_latencies):.2f} ms")
    print(f"Best:    {min(push_latencies):.2f} ms")
    print(f"Worst:   {max(push_latencies):.2f} ms\n")

    print("Total Notification Latency (POST → WS recv):")
    print(f"Average: {sum(total_latencies)/len(total_latencies):.2f} ms")
    print(f"Best:    {min(total_latencies):.2f} ms")
    print(f"Worst:   {max(total_latencies):.2f} ms")


if __name__ == "__main__":
    main()
