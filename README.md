Distributed Inference Engine
A production-style ML inference system built around a distributed worker pool, Redis task queue, and a FastAPI gateway. Designed from the ground up for fault tolerance and horizontal scalability.
The core idea: instead of handling prediction requests synchronously in a single process, the gateway enqueues jobs into Redis and a pool of independent workers competes to process them. When a worker crashes mid-job, the watchdog detects the missed heartbeat, respawns the worker, and the job is automatically re-queued — no requests are lost.
Prerequisites

Initial Run 
<img width="629" height="179" alt="image" src="https://github.com/user-attachments/assets/ec3911a5-b66c-40c3-933a-8f6e690488af" />

PS: This is how the project is for now it uses a basic model and uses only 3 workers for now I'll update the project as I make improvements
Python 3.10+
Docker (for Redis) or a local Redis install

1. Start Redis
bashdocker run -d -p 6379:6379 --name redis redis:latest
2. Install dependencies
bashpip install fastapi uvicorn redis scikit-learn numpy requests
3. Train the model
bashpython model.py
4. Run the system
Open three terminals:
bash# Terminal 1 — API gateway
uvicorn main:app --reload

# Terminal 2 — worker pool + watchdog
python watchdog.py

# Terminal 3 — load test
python load_test.py
5. Check metrics
http://localhost:8000/metrics

Project Structure
├── main.py          # FastAPI gateway — /predict, /result, /metrics
├── worker.py        # Worker process — pops jobs, runs inference, stores results
├── watchdog.py      # Spawns workers, monitors heartbeats, auto-restarts on failure
├── model.py         # Trains and loads sklearn RandomForest model
├── load_test.py     # Concurrent load tester with P50/P95/P99 reporting
└── README.md

