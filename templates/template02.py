#!/usr/bin/env python3

import sys, os, datetime

os.system('cls' if os.name == 'nt' else 'clear')
print('Started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# your code

print('Stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('\a', end='', file=sys.stderr)
