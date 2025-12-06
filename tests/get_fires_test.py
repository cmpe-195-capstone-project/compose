import requests
import time

BASE_URL = "http://<AWS_IP>"
get_url = f'{BASE_URL}/test/fires'
post_url = f'{BASE_URL}/test/fire-w-coords'
delete_url = f'{BASE_URL}/test/fire'

latencies = []

fire_payload = {
    "longitude": -121.875329832,
    "latitude": 37.334665328
}

def test1():
    for i in range(500):
        print(f"Epoch {i + 1}")

        # timestamp BEFORE request
        start_time = time.time()

        # POST request (simulating a new fire popping up)
        post_res = requests.post(post_url, json=fire_payload)
        if post_res.status_code != 200:
            print("POST FAILED:", post_res.text)
            continue
        

        # GET request (user gets latest fire info)
        get_res = requests.get(get_url)
        end_time = time.time()    

        fires = get_res.json()
        fire_id = fires[0].get("id")

        # timestamp AFTER response arrives 
        latency_ms = (end_time - start_time) * 1000
        latencies.append(latency_ms)
    

        # DELETE request 
        delete_res = requests.delete(f"{delete_url}/{fire_id}")
        print("Deleted Code:", delete_res.status_code)

        print(f"Latency: {latency_ms:.2f} ms\n")

    avg = sum(latencies) / len(latencies)
    print("\n--- RESULTS ---")
    print(f"Average: {avg:.2f} ms")
    print(f"Best:    {min(latencies):.2f} ms")
    print(f"Worst:   {max(latencies):.2f} ms")


test1()