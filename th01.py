import threading
import time

def worker(num):
    print(f"Worker {num} started")
    for i in range(5):
        print(f"Worker {num}: iteration {i+1}")
        time.sleep(0.5)
    print(f"Worker {num} finished")

if __name__ == "__main__":
    threads = []
    num_threads = 5

    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
