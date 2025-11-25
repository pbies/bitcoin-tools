#!/usr/bin/env python3

import os
import glob
from tqdm import tqdm

for path in glob.glob("*.txt"):
	print(path)
	with open(path, "rb") as f:
		lines = f.readlines()
	with open(path, "wb") as f:
		for line in tqdm(lines):
			f.write(line.strip() + b"\n")
