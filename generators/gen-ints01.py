#!/usr/bin/env python3

import sys, os, datetime, time

start_msg=''
start_time=0

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(__file__)
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	global start_time
	start_time=time.time()

	o=open('output.txt','w')
	for y in range(1, 100000001):
		o.write(f'{y}\n')

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

# https://stackoverflow.com/questions/5925918/python-suppressing-errors-from-going-to-commandline
def supressErrors(*args):
	pass

if __name__ == '__main__':
	sys.tracebacklimit = 0
	sys.stderr = supressErrors()
	try:
		main()
	except KeyboardInterrupt:
		print('\nKeyboard break!\a')
		stop_time=time.time()
		print(start_msg)
		print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
		print('\a', end='', file=sys.stderr)
		try:
			sys.exit(130)
		except:
			os._exit(130)
