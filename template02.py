#!/usr/bin/env python3

import sys, os, datetime

os.system('cls' if os.name == 'nt' else 'clear')
print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# your code

print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print('\a', end='', file=sys.stderr)
