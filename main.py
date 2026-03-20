import redis, uuid, json, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

QUEUE_KEY = "job_queue"
PROCESSING_KEY = "job_processing"

class PredictRequest(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(req: PredictRequest):
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "features": req.features,
        "enqueued_at": time.time()
    }
    # Push job to queue
    r.rpush(QUEUE_KEY, json.dumps(job))
    # Track queue depth metric
    r.incr("metrics:total_enqueued")
    return {"job_id": job_id, "status": "queued"}

@app.get("/result/{job_id}")
def get_result(job_id: str):
    result = r.get(f"result:{job_id}")
    if result is None:
        return {"job_id": job_id, "status": "pending"}
    return {"job_id": job_id, "status": "done", "result": json.loads(result)}

@app.get("/metrics")
def get_metrics():
    # Queue depth
    queue_depth = r.llen(QUEUE_KEY)

    # Worker heartbeats
    worker_keys = r.keys("worker:*:heartbeat")
    active_workers = len(worker_keys)

    # Latency percentiles from sorted set
    latencies = r.zrange("metrics:latencies", 0, -1, withscores=True)
    times = [score for _, score in latencies]

    p50 = p95 = p99 = 0
    if times:
        times.sort()
        n = len(times)
        p50 = round(times[int(n * 0.50)], 3)
        p95 = round(times[int(n * 0.95)], 3)
        p99 = round(times[int(n * 0.99)], 3)

    return {
        "queue_depth": queue_depth,
        "active_workers": active_workers,
        "total_jobs_processed": r.get("metrics:total_processed") or 0,
        "latency_ms": {"p50": p50, "p95": p95, "p99": p99}
    }