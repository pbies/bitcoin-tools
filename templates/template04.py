#!/usr/bin/env python3

import sys, os, datetime, time

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	# your code

	stop_time=time.time()
	print('Stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
