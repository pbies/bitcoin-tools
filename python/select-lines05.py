#!/usr/bin/env python3

import sys
import threading
from queue import Queue

NUM_WORKERS = 4
BLOCK_SIZE = 11
SENTINEL = None

input_queue = Queue(maxsize=NUM_WORKERS * 2)
output_queue = Queue(maxsize=NUM_WORKERS * 2)


def reader(input_path):
	"""Read blocks of BLOCK_SIZE lines and enqueue them with their block index."""
	with open(input_path, 'r') as f:
		block_index = 0
		while True:
			block = []
			for _ in range(BLOCK_SIZE):
				line = f.readline()
				if not line:
					break
				block.append(line)
			if not block:
				break
			input_queue.put((block_index, block))
			block_index += 1
	# Signal workers to stop
	for _ in range(NUM_WORKERS):
		input_queue.put(SENTINEL)


def worker():
	"""Process blocks: skip the first line, pass the rest to output."""
	while True:
		item = input_queue.get()
		if item is SENTINEL:
			output_queue.put(SENTINEL)
			break
		block_index, block = item
		# Skip first line of each block (index 0), write the rest
		processed = block[1:]
		output_queue.put((block_index, processed))


def writer(output_path, num_workers):
	"""Collect processed blocks and write them in order."""
	buffer = {}
	next_index = 0
	done_workers = 0

	with open(output_path, 'w') as f:
		while done_workers < num_workers:
			item = output_queue.get()
			if item is SENTINEL:
				done_workers += 1
				continue
			block_index, lines = item
			buffer[block_index] = lines
			# Write any consecutive blocks that are ready
			while next_index in buffer:
				for line in buffer.pop(next_index):
					f.write(line)
				next_index += 1


# Start reader thread
r_thread = threading.Thread(target=reader, args=('output.txt',), daemon=True)
r_thread.start()

# Start worker threads
w_threads = []
for _ in range(NUM_WORKERS):
	t = threading.Thread(target=worker, daemon=True)
	t.start()
	w_threads.append(t)

# Run writer in main thread
writer('output3.txt', NUM_WORKERS)

r_thread.join()
for t in w_threads:
	t.join()

print('\a', end='', file=sys.stderr)
