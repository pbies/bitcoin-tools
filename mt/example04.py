#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor
import requests
import time

def fetch(url):
	response = requests.get(url)
	print(f"{url}: {response.status_code}")

urls = [
	"https://www.google.com",
	"https://www.python.org",
	"https://www.github.com",
	"https://www.stackoverflow.com"
]

start = time.time()

with ThreadPoolExecutor(max_workers=4) as executor:
	executor.map(fetch, urls)

print(f"Total time: {time.time() - start:.2f} seconds")
