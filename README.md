# Distributed Inference Engine

A production-style ML inference system built around a distributed worker pool, Redis task queue, and a FastAPI gateway.

The problem this solves is straightforward: if you run inference synchronously in a single process, one slow request blocks everything behind it. This system decouples request intake from computation entirely. The gateway accepts a job, drops it into a Redis queue, and returns a job ID immediately. Workers sit in a loop waiting for jobs, grab whatever is next, run inference, and write the result back. The client polls for completion.

The more interesting part is what happens when things break. Workers crash — that's a given in any real system. Rather than treating it as an edge case, fault tolerance is built into the core design. Every worker emits a heartbeat to Redis every few seconds with a short TTL. A watchdog process monitors those keys; if one goes missing, it respawns the worker automatically. Jobs use Redis's `RPOPLPUSH` reliable queue pattern, so nothing in-flight gets dropped when a worker dies.

---

## Initial Run
Results for the first run with three workers. 

PS: The project will get some updates in a few days this is just the first run.

<img width="629" height="179" alt="image" src="https://github.com/user-attachments/assets/57d1c471-978e-4483-8dfd-55e2e4e2077d" />

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for Redis) or a local Redis install

### 1. Start Redis
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### 2. Install dependencies
```bash
pip install fastapi uvicorn redis scikit-learn numpy requests
```

### 3. Train the model
```bash
python model.py
```

### 4. Run the system

Open three terminals:
```bash
# Terminal 1 — API gateway
uvicorn main:app --reload

# Terminal 2 — worker pool + watchdog
python watchdog.py

# Terminal 3 — load test
python load_test.py
```

### 5. Check metrics
```
http://localhost:8000/metrics
```

---

## Project Structure
```
├── main.py          # FastAPI gateway — /predict, /result, /metrics
├── worker.py        # Worker process — pops jobs, runs inference, stores results
├── watchdog.py      # Spawns workers, monitors heartbeats, auto-restarts on failure
├── model.py         # Trains and loads sklearn RandomForest model
├── load_test.py     # Concurrent load tester with P50/P95/P99 reporting
└── README.md
```

---
