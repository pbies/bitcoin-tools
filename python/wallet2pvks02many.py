#!/usr/bin/env python3

import sys, os, datetime, time
import glob

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	for path in glob.glob("*.dat"):
		print(f'Processing {path}...')
		i=open(path,'rb').read()
		o=open(path+'.txt','w')
		for idx in range(0, len(i)-32-8):
			x=i[idx:idx+5]
			if x==b'\x02\x01\x01\x04\x20':
				y=i[idx+5:idx+5+32]
				o.write(y.hex()+'\n')

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
