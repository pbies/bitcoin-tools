#!/usr/bin/env python3

import sys, os, datetime, time

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	i=open('input.txt','r').read().splitlines()
	for j in i:
		w=f'{j}\n{j[2:]}\n{j.lower()}\n{j[2:].lower()}\n'
		with open('output.txt','a') as o:
			o.write(w)

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
