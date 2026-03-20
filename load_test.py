import requests, time, json
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://localhost:8000"
FEATURES = [5.1, 3.5, 1.4, 0.2]  # iris sample
NUM_REQUESTS = 200
CONCURRENCY = 20

def send_request():
    start = time.time()
    r = requests.post(f"{BASE_URL}/predict", json={"features": FEATURES})
    job_id = r.json()["job_id"]

    # Poll for result
    for _ in range(50):
        res = requests.get(f"{BASE_URL}/result/{job_id}")
        if res.json()["status"] == "done":
            return (time.time() - start) * 1000
        time.sleep(0.05)
    return None

def run_load_test():
    print(f"Firing {NUM_REQUESTS} requests at concurrency {CONCURRENCY}...")
    latencies = []

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request) for _ in range(NUM_REQUESTS)]
        for f in as_completed(futures):
            result = f.result()
            if result:
                latencies.append(result)

    latencies.sort()
    n = len(latencies)
    print(f"\nResults ({n} completed):")
    print(f"  P50:  {latencies[int(n*0.50)]:.1f}ms")
    print(f"  P95:  {latencies[int(n*0.95)]:.1f}ms")
    print(f"  P99:  {latencies[int(n*0.99)]:.1f}ms")
    print(f"  Throughput: {n / (sum(latencies)/1000/n * n):.1f} req/s")

if __name__ == "__main__":
    run_load_test()