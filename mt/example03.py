#!/usr/bin/env python3

import threading
import requests
import time

def fetch_url(url):
	response = requests.get(url)
	print(f"{url}: {response.status_code}")

urls = [
	"https://www.google.com",
	"https://www.python.org",
	"https://www.github.com",
	"https://www.stackoverflow.com"
]

start = time.time()
threads = []

for url in urls:
	thread = threading.Thread(target=fetch_url, args=(url,))
	thread.start()
	threads.append(thread)

for thread in threads:
	thread.join()

print(f"Total time: {time.time() - start:.2f} seconds")
