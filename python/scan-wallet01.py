#!/usr/bin/env python3

import sys, os, datetime, time
from tqdm import tqdm

l=32 # bytes

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	infile=open('input.dat','rb').read()
	outfile=open('output.txt','w')
	cnt=len(infile)
	k=set()
	for i in tqdm(range(0,cnt-l+1)):
		k.add(infile[i:i+l].hex()+'\n')

	s=sorted(k)

	for i in tqdm(s):
		outfile.write(i)

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
