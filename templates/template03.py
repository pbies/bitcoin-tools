#!/usr/bin/env python3

import sys, os, datetime, time

os.system('cls' if os.name == 'nt' else 'clear')
print('Started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
start_time=time.time()

# your code

print('Stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
stop_time=time.time()
print(f'Execution took: {stop_time-start_time:.3f} seconds')
print('\a', end='', file=sys.stderr)
