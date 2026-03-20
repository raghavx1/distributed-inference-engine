import redis, json, time, os, sys
from model import load_model, predict

def run_worker(worker_id: int):
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)
    model = load_model()

    QUEUE_KEY = "job_queue"
    PROCESSING_KEY = f"job_processing:{worker_id}"
    HEARTBEAT_KEY = f"worker:{worker_id}:heartbeat"

    print(f"[Worker {worker_id}] Started, PID: {os.getpid()}")

    while True:
        # Send heartbeat every iteration — expires in 5s
        r.setex(HEARTBEAT_KEY, 5, os.getpid())

        # BLPOP blocks until a job arrives (timeout 2s so heartbeat keeps updating)
        job_raw = r.blpop(QUEUE_KEY, timeout=2)
        if job_raw is None:
            continue

        _, job_str = job_raw
        job = json.loads(job_str)
        job_id = job["job_id"]

        # Move to processing key for fault tolerance
        r.set(PROCESSING_KEY, job_str, ex=30)

        start = time.time()
        try:
            prediction = predict(model, job["features"])
            latency_ms = (time.time() - start) * 1000

            # Store result for client
            result = {
                "prediction": prediction,
                "worker_id": worker_id,
                "latency_ms": round(latency_ms, 3)
            }
            r.set(f"result:{job_id}", json.dumps(result), ex=300)

            # Track metrics
            r.zadd("metrics:latencies", {job_id: latency_ms})
            r.incr("metrics:total_processed")

            print(f"[Worker {worker_id}] Job {job_id[:8]} done in {latency_ms:.1f}ms")

        except Exception as e:
            print(f"[Worker {worker_id}] Error on job {job_id}: {e}")

        finally:
            # Clear processing key — job is done
            r.delete(PROCESSING_KEY)

if __name__ == "__main__":
    worker_id = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    run_worker(worker_id)