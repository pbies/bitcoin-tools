#!/usr/bin/env python3

# https://github.com/TheSpeedX/PROXY-List/blob/master/http.txt => live.txt

import os
import requests
import threading
import random
import time

# Configuration
url = 'https://ftp.icm.edu.pl/pub/Linux/ubuntu-releases/noble/ubuntu-24.04.2-desktop-amd64.iso' # you can replace it with target url
output_file = 'ubuntu-24.04.2-desktop-amd64.iso' # file name
proxy_file = 'live.txt' # replace it with your proxy file, proxy format: type://address:port
num_threads = 16 # more thread = faster downloading = better internet speed needed
thr=num_threads
# batch_size = 1024 * 300 # 100 KB

# Global variables
lock = threading.Lock()
downloaded_parts = []

def download_part(start, end, thread_id):
	while True:
		proxy = get_random_proxy()
		try:
			headers = {'Range': f'bytes={start}-{end}'}
			response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=5)
			response.raise_for_status()
			data = response.content
			with lock:
				insert_downloaded_part(start, data)
				write_to_file(start, data)
				global thr
				thr=thr-1
				print(f'Threads left: {thr}   \r',end='')
			break
		except requests.exceptions.RequestException as e:
			pass
			# print(f'Thread {thread_id} failed with proxy {proxy}. Retrying with a different proxy.')

def get_random_proxy():
	with open(proxy_file, 'r') as file:
		proxies = file.read().splitlines()
	return random.choice(proxies)

def insert_downloaded_part(start, data):
	downloaded_parts.append((start, data))
	downloaded_parts.sort(key=lambda x: x[0])

def write_to_file(start, data):
	with open(output_file, 'r+b') as file:
		file.seek(start)
		file.write(data)

def main():
	# Get the file size
	response = requests.head(url)
	file_size = int(response.headers['Content-Length'])

	# Allocate the output file
	with open(output_file, 'wb') as file:
		file.seek(file_size - 1)
		file.write(b'\0')

	# Calculate the part size and ranges
	part_size = file_size // num_threads
	ranges = []
	for i in range(num_threads):
		start = i * part_size
		end = start + part_size - 1 if i < num_threads - 1 else file_size - 1
		ranges.append((start, end))

	start_time = time.time()

	# Create and start the threads
	threads = []
	for i, (start, end) in enumerate(ranges):
		thread = threading.Thread(target=download_part, args=(start, end, i))
		thread.start()
		threads.append(thread)
	 

	print("Running %d Threads...." % len(threads))
	
	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	end_time = time.time()
	diff = end_time - start_time

	print('File downloaded successfully.\a')
	print(f'Time: {int(diff/60)}m{diff%60:.3f}s')

if __name__ == '__main__':
	main()
