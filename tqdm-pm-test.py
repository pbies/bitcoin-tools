#!/usr/bin/env python3

from tqdm import tqdm
import time
from tqdm.contrib.concurrent import process_map

def go(i):
	time.sleep(.001)

process_map(go, range(1,40001), max_workers=4, chunksize=1000)

import sys
print('\a',end='',file=sys.stderr)
