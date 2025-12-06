from websocket import create_connection
import json, requests, time
from collections import defaultdict
import random

BASE_WS_URL = "ws://<AWS_IP>"
BASE_URL = "http://<AWS_IP>"

ws_url = f"{BASE_WS_URL}/ws/alert?id="
test_user_id = 98

post_url = f"{BASE_URL}/test/fire-w-coords"
delete_url = f"{BASE_URL}/test/fire"

location_payload = {
    "type": "update_location",
    "longitude": -121.875329832,
    "latitude": 37.334665328
}

# Fire inside the bounding box
fire_in_bbox_payload = {
    "latitude": 37.33466533,
    "longitude": -121.87532983
}

push_latencies = []
total_latencies = []

def test2():
    for i in range(2):
        time.sleep(0.5)
        print(f"Epoch {i + 1}")

        # coonect to ws
        ws = create_connection(f"{ws_url}{test_user_id}")

        # send (push) location on ws conn 
        push_start = time.time()
        ws.send(json.dumps(location_payload))
        push_end = time.time()

        delay = random.uniform(0, 30)
        print(f"Sleeping {delay:.2f} seconds before fire insert...")
        time.sleep(delay)

        push_latency_ms = (push_end - push_start) * 1000
        push_latencies.append(push_latency_ms)

        print(f"WS Send Latency: {push_latency_ms:.2f} ms")

        # start the total latency
        total_start = time.time()
        # POST request (simulating a new fire popping up in bbox)
        post_res = requests.post(post_url, json=fire_in_bbox_payload)
        if post_res.status_code != 200:
            print("POST FAILED:", post_res.text)
            ws.close()
            return

        fire_id = post_res.json().get("id")

        # wait for ws message and end timer
        ws_msg = ws.recv()
        total_end = time.time()

        total_latency_ms = (total_end - total_start) * 1000
        total_latencies.append(total_latency_ms)

        print(f"TOTAL Latency: {total_latency_ms:.2f} ms")


        # DELETE request (clean up) 
        requests.delete(f"{delete_url}/{fire_id}")


        ws.close()
        time.sleep(0.5)
    print("\n--- Results ---")

    # pushing to ws latency report
    print("Pushing to ws:")
    print(f"Average: {sum(push_latencies)/len(push_latencies):.2f} ms")
    print(f"Best:    {min(push_latencies):.2f} ms")
    print(f"Worst:   {max(push_latencies):.2f} ms\n")

    # total latency report
    print("Total Notification Latency:")
    print(f"Average: {sum(total_latencies)/len(total_latencies):.2f} ms")
    print(f"Best:    {min(total_latencies):.2f} ms")
    print(f"Worst:   {max(total_latencies):.2f} ms\n")

test2()