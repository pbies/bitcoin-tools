#!/usr/bin/env python3

from multiprocessing import Pool
import tqdm

def do_work(x):
	pass

tasks=range(1,10001)

if __name__ == "__main__":
	pool = Pool(processes=8)
	for _ in tqdm.tqdm(pool.imap_unordered(do_work, tasks, chunksize=1000), total=len(tasks)):
		pass
