#!/usr/bin/env python3

import sys, os, datetime, time

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	i=open('input.txt','r')
	o=open('output.txt','w')
	while True:
		w=[]
		for a in range(10):
			t=i.readline()
			if not t:
				break
			w.append(t)
		o.write(w[3]+w[4]+w[5]+w[6]+w[7]+w[8])

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
