#!/usr/bin/env python3

import sys, os, datetime, time
from tqdm import tqdm

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	start_msg='Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time=time.time()

	i=open('input.txt','r')
	o=open('output.txt','w')

	total_bytes=os.path.getsize('input.txt')
	read_bytes=0

	if total_bytes>0:
		pbar=tqdm(total=total_bytes, unit='B', unit_scale=True, desc='Reading')
	else:
		pbar=None

	while True:
		w=[]
		for a in range(10):
			t=i.readline()
			if not t:
				break
			inc=len(t.encode())
			read_bytes+=inc
			if pbar is not None:
				pbar.update(inc)
			w.append(t)

		if not w:
			break

		try:
			o.write(w[3]+w[4]+w[5]+w[6]+w[7]+w[8])
		except IndexError:
			pass

	if pbar is not None:
		pbar.close()

	i.close()
	o.close()

	stop_time=time.time()
	print(start_msg)
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time-start_time))}')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
