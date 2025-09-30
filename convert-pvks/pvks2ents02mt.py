#!/usr/bin/env python3

from multiprocessing import Pool
from tqdm import tqdm
import sys, os, datetime, time

def _fast_count_lines(path: str, bufsize: int = 1024 * 1024) -> int:
	cnt = 0
	with open(path, 'rb', buffering=bufsize) as f:
		while True:
			chunk = f.read(bufsize)
			if not chunk:
				break
			cnt += chunk.count(b'\n')
	try:
		if cnt == 0:
			with open(path, 'rb') as g:
				for _ in g:
					cnt += 1
			return cnt
		with open(path, 'rb') as g:
			g.seek(-1, os.SEEK_END)
			if g.read(1) != b'\n':
				cnt += 1
	except OSError:
		pass
	return cnt

def go(x):
	y=x.rstrip(b'\n')
	a,b=x[0:32],x[32:]
	with open('output.txt','a') as o:
		w=f'{a.decode()}\n{b.decode()}'
		o.write(w)

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print('Program started: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	start_time=time.time()

	i=open('input.txt','rb')
	# l=os.path.getsize('input.txt')
	l=_fast_count_lines('input.txt')

	open('output.txt', 'w').close()

	c=1000
	t=0
	with Pool(processes=24) as p, tqdm(total=l) as pbar: # , unit='B', unit_scale=True
		for result in p.imap_unordered(go, i, chunksize=1000):
			t=t+1
			if t==c:
				pbar.update(c)
				pbar.refresh()
				t=0

	stop_time=time.time()
	print('Program stopped: '+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {stop_time-start_time:.3f} seconds')
	print('\a', end='', file=sys.stderr)

if __name__=='__main__':
	main()
