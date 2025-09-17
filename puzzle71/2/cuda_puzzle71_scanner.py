#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CUDA Puzzle71 scanner (GPU wrapper for keyhunt-cuda)

What it does
------------
- Keeps your original "random chunk in range" workflow.
- Offloads the actual HASH160 search to GPU via keyhunt-cuda (orders of magnitude faster).
- Streams keyhunt output, detects hits, logs neatly, and beeps on success.
- Works with compressed pubkeys (p2pkh HASH160).

Requirements
------------
1) NVIDIA GPU + CUDA drivers installed
2) keyhunt (CUDA build) available on PATH, e.g. compiled with: make cuda
   Popular repo name is often "keyhunt" (by iceland2k/Iceaxe forks). Use a CUDA-enabled build.
3) Python packages: tqdm

Usage
-----
- Set TARGET_RMD160 to the 20-byte HASH160 (hex) you want to find (already set from your script).
- Adjust global config below if needed.
- Run: python3 cuda_puzzle71_scanner.py

Notes
-----
- This wrapper calls keyhunt for each random subrange. keyhunt will internally use the GPU.
- You can tweak KEYHUNT_ARGS to squeeze more speed depending on your GPU.
"""
import datetime, os, random, shutil, signal, sys, time, subprocess
from pathlib import Path
from tqdm import tqdm

# ----------------- USER CONFIG (tune to taste) -----------------
# Full search space (taken from your original script)
RANGE_START = 0x400000000000000000
RANGE_END   = 0x7fffffffffffffffff

# One random chunk size per iteration (bigger -> fewer launches, more GPU work per run)
RANGE_SIZE  = 2**28  # default 268,435,456 keys per chunk (adjust to your VRAM/time)

# HASH160 target (20 bytes, hex) — from your script
TARGET_RMD160 = 'f6f5431d25bbf7b12e8add9af5e3475c44a0a5b8'

# Number of random chunks to try before stopping (None for endless loop)
NUM_CHUNKS = None

# Keyhunt binary name/path (must be CUDA build). If not on PATH, set absolute path here.
KEYHUNT_BIN = shutil.which('keyhunt') or 'keyhunt'

# Keyhunt tuning flags:
# -m rmd160    : search by HASH160
# -q           : quiet banner
# -g           : use GPU (CUDA)
# --gpui 0     : choose GPU id (0 by default). For multi-GPU, pass multiple --gpui flags.
# --keyspace   : inclusive start:end hex range (64-hex wide, zero-padded)
# -f           : file with targets (we'll use --rmd160 directly instead of file)
# -c           : compressed pubkeys (p2pkh hash160 of compressed pubkey)
# -t           : GPU threads per block / tuning (keyhunt uses its own params; leave None to omit)
#
# You can add more flags if your keyhunt build supports them.
KEYHUNT_ARGS = [
	'-m', 'rmd160',
	'-g',
	'--gpui', '0',
	'-c',
	'-q',
]

# Optional: pass threads-per-block (uncomment and tune if supported by your build)
# KEYHUNT_ARGS += ['-t', '512']

# Progress bar granularity: how many keys "count" as one step on the tqdm bar.
# (Only affects the visual; keyhunt does the real work.)
PBAR_STEP = 1_000_000

# Log file
LOG_FILE = 'log_gpu.txt'
# ---------------------------------------------------------------

def log(msg: str) -> None:
	timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	line = f'{timestamp} {msg}'
	print(line, flush=True)
	with open(LOG_FILE, 'a', encoding='utf-8') as f:
		f.write(line + '\n')

def beep():
	try:
		# Terminal bell
		print('\a', end='', file=sys.stderr, flush=True)
	except Exception:
		pass

def have_keyhunt() -> bool:
	if not shutil.which(KEYHUNT_BIN):
		# Try if user set absolute/relative path
		return Path(KEYHUNT_BIN).exists() and os.access(KEYHUNT_BIN, os.X_OK)
	return True

def hex64(n: int) -> str:
	"""Return 64-hex string (zero-padded)."""
	return f'{n:064x}'

def call_keyhunt(start_int: int, end_int: int, target_hex: str) -> bool:
	"""
	Calls keyhunt over [start_int, end_int] inclusive.
	Returns True if found; False otherwise.
	Parses stdout lines for a 'FOUND' marker (depends on keyhunt build).
	"""
	keyspace = f'{hex64(start_int)}:{hex64(end_int)}'

	cmd = [KEYHUNT_BIN, '--keyspace', keyspace, '--rmd160', target_hex] + KEYHUNT_ARGS

	log(f'Launching keyhunt: {" ".join(cmd)}')
	start_time = time.time()

	# Spawn process and stream stdout
	with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True) as proc:
		found = False
		pbar_total_steps = max(1, (end_int - start_int + 1) // PBAR_STEP)
		with tqdm(total=pbar_total_steps, desc='GPU chunk', unit='step') as pbar:
			for line in proc.stdout:
				line = line.rstrip('\n')
				# Heuristic: update bar occasionally (many builds print progress lines)
				if line:
					# Try to extract progress when keyhunt prints something like "X / Y"
					if '/' in line:
						try:
							left, right = line.split('/', 1)
							cur = int(''.join(ch for ch in left if ch.isdigit()) or 0)
							total = int(''.join(ch for ch in right if ch.isdigit()) or 0)
							if total > 0:
								steps = (cur // PBAR_STEP) - pbar.n
								if steps > 0:
									pbar.update(steps)
						except Exception:
							pass
					else:
						# No explicit progress; tick occasionally
						if random.random() < 0.01:
							if pbar.n < pbar.total:
								pbar.update(1)

					# Detect a "FOUND" line.
					# Different forks print slightly different strings; match common patterns.
					if 'FOUND' in line.upper() or 'WIF:' in line.upper() or 'PVK:' in line.upper():
						log(f'[keyhunt] {line}')
						found = True
				# Echo raw line for logs (optional; comment if too verbose)
				# log(f'[keyhunt] {line}')

		# Ensure process ended
		ret = proc.wait()

	elapsed = time.time() - start_time
	log(f'keyhunt finished (rc={ret}) in {elapsed:.2f}s')

	return found

def main():
	os.system('cls||clear')
	print('CUDA Puzzle 71 scanner – GPU (keyhunt)')

	if not have_keyhunt():
		print('ERROR: CUDA-enabled keyhunt binary not found.')
		print('• Put compiled CUDA build on PATH as "keyhunt", or set KEYHUNT_BIN path in this script.')
		sys.exit(2)

	random.seed()  # real entropy

	chunk_no = 0
	try:
		while True:
			# Pick a random chunk entirely within the global range
			start_range = random.randint(RANGE_START, max(RANGE_START, RANGE_END - RANGE_SIZE))
			end_range   = min(RANGE_END, start_range + RANGE_SIZE - 1)

			print(f'\nChunk #{chunk_no} -> {hex(start_range)[2:]}:{hex(end_range)[2:]}')
			log(f'Chunk {chunk_no} start={hex64(start_range)} end={hex64(end_range)} size={end_range-start_range+1:,}')

			found = call_keyhunt(start_range, end_range, TARGET_RMD160)

			if found:
				log('*** HIT! Target located in this chunk. Check the last [keyhunt] line(s) above for the private key/WIF.')
				beep()
				break

			chunk_no += 1
			if NUM_CHUNKS is not None and chunk_no >= NUM_CHUNKS:
				log('Stopping after reaching NUM_CHUNKS limit.')
				break

	except KeyboardInterrupt:
		print('\nAborted by user.')
		log('Interrupted by user (SIGINT).')
		sys.exit(130)

if __name__ == '__main__':
	main()
