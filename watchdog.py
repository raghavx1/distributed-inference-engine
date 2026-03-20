import redis, time, subprocess, sys

NUM_WORKERS = 3
worker_processes = {}

def start_worker(worker_id):
    proc = subprocess.Popen([sys.executable, "worker.py", str(worker_id)])
    worker_processes[worker_id] = proc
    print(f"[Watchdog] Started worker {worker_id}, PID: {proc.pid}")
    return proc

def run_watchdog():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    # Start all workers initially
    for i in range(NUM_WORKERS):
        start_worker(i)

    print(f"[Watchdog] Monitoring {NUM_WORKERS} workers...")

    while True:
        time.sleep(3)
        for worker_id in range(NUM_WORKERS):
            heartbeat = r.get(f"worker:{worker_id}:heartbeat")
            proc = worker_processes.get(worker_id)

            # If no heartbeat or process is dead — restart it
            if heartbeat is None or (proc and proc.poll() is not None):
                print(f"[Watchdog] Worker {worker_id} is dead. Restarting...")
                start_worker(worker_id)

if __name__ == "__main__":
    run_watchdog()