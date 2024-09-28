#!/usr/bin/env python3

from tqdm import tqdm
import time

for i in tqdm(range(0,400), ncols=132):
	time.sleep(.05)

import sys
print('\a',end='',file=sys.stderr)
