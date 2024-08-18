#!/usr/bin/env python3

from tqdm import tqdm
import time

for i in tqdm(range(0,400)):
	time.sleep(.1)

import sys
print('\a',end='',file=sys.stderr)
