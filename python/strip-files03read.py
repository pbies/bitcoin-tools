#!/usr/bin/env python3

import os
import glob
import sys
from tqdm import tqdm
from pathlib import Path

def _get_file_size(file_path: str) -> int:
	"""Get file size in bytes."""
	return os.path.getsize(file_path)

def main():
	for path in glob.glob("*.txt"):
		print(path)
		file_size = _get_file_size(path)
		
		with open(path, "rb") as f:
			with open(path + '.out', "wb") as g:
				# Create progress bar with total file size
				with tqdm(total=file_size, unit='B', unit_scale=True, desc="Processing") as pbar:
					while True:
						line = f.readline()
						if not line:  # End of file
							break
						
						# Write stripped line with newline
						g.write(line.strip() + b"\n")
						
						# Update progress bar with bytes read
						current_pos = f.tell()
						pbar.update(current_pos - pbar.n)  # Update by difference
					
					# Ensure progress bar reaches 100% at the end
					pbar.update(file_size - pbar.n)

	print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
	main()
