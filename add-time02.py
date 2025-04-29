#!/usr/bin/env python3

import datetime
import sys

for line in sys.stdin:
	timestamp = datetime.datetime.now().strftime("%F %T.%f")[:-3]
	print(f'{timestamp} {line}', end='')
