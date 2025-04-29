#!/usr/bin/env python3

import datetime
import fileinput

for line in fileinput.input():
	timestamp = datetime.datetime.now().strftime("%F %T.%f")[:-3]
	print(f'{timestamp} {line}', end='')
