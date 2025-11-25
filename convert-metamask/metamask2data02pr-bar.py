#!/usr/bin/env python3

import sys, os, datetime, time, json
from tqdm import tqdm

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	i=open('input.txt','r').readlines()
	o=open('output.txt','w')
	for line in tqdm(i):
		d=line.rstrip('\n').split('$')
		salt=d[2]
		iv=d[3]
		data=d[4]
		out={'data':data,'iv':iv,'salt':salt}
		o.write(json.dumps(out)+'\n')

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
