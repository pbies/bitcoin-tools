#!/usr/bin/env python3

import sys, os, datetime, time

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	# your code

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
