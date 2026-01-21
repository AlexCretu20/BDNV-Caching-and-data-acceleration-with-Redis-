import time
import threading
import requests

BASE = "http://127.0.0.1:5000"
URLS = [
    f"{BASE}/restaurants?city=Paris",
    f"{BASE}/cafes?city=Paris",
]

DURATION_SEC = 60      
THREADS = 20          

stop = False
ok = 0
err = 0
lock = threading.Lock()

def worker():
    global ok, err
    i = 0
    while not stop:
        url = URLS[i % len(URLS)]
        i += 1
        try:
            r = requests.get(url, timeout=10)
            with lock:
                if r.status_code == 200:
                    ok += 1
                else:
                    err += 1
        except Exception:
            with lock:
                err += 1

def main():
    global stop
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(THREADS)]
    for t in threads:
        t.start()

    start = time.time()
    time.sleep(DURATION_SEC)
    stop = True
    time.sleep(1)

    elapsed = time.time() - start
    with lock:
        total = ok + err
        rps = total / elapsed if elapsed > 0 else 0

    print(f"Threads: {THREADS}")
    print(f"Duration: {DURATION_SEC}s")
    print(f"Total requests: {total}  OK: {ok}  ERR: {err}")
    print(f"Approx RPS: {rps:.2f}")

if __name__ == "__main__":
    main()
