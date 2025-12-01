#!/usr/bin/env python3

import sys, os, datetime, time
from tqdm import tqdm

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	i=open('02.txt','r')
	o=open('03.txt','w')
	for x in tqdm(i):
		x=x.strip()
		for y in range(len(x)-63):
			o.write(x[y:y+64]+'\n')

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
