#!/usr/bin/env python3

from tqdm import tqdm
from tqdm.contrib.concurrent import process_map
import base58, re
import os, sys, hashlib

def go(x):
	with open('output.txt','a') as outfile:
		outfile.write(x)

print('Reading...', flush=True)
lines = set(open('input.txt','r').read().splitlines())

print('Writing...', flush=True)
open('output.txt', 'w').close()
process_map(go, lines, max_workers=24, chunksize=1000)

print('\a', end='', file=sys.stderr)
