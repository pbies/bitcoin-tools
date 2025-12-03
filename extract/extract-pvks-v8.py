#!/usr/bin/env python3

import sys, os, datetime, time
from tqdm import tqdm

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	i=open('input.txt','rb').read()
	o=open('output.txt','w')
	c=len(i)
	for pos in range(0,c-31):
		d=i[pos:pos+32]
		o.write(d.hex()+'\n')

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
