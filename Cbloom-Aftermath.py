#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bloom_filter2 import BloomFilter
import sys

def count_lines(file):
	return sum(1 for line in open(file, 'r'))

def add_to_bf(file, nom, bf_filter):
	i = 0
	line_10 = 100000
	f = open(file)
	while i < nom:
		if line_10 == i:
			print("Total line ->" + str(line_10), end='\r')
			line_10 += 100000
		text = f.readline().strip()
		if text[:2] == '0x': bf_filter.add(text.lower()[2:])
		else: bf_filter.add(text)
		i += 1
	f.close()
	return i

def bloom_filter():
	print("[I] Bloom Filter START")
	print("[I] File input -> " + file_txt)
	print("[I] File output -> " + file_bf)
	bf = BloomFilter(max_elements=line_count, error_rate=1e-16, filename=(file_bf, -1))

	print("[I] ADD Bloom Filter")
	added=add_to_bf(file_txt, line_count, bf)

	# Print several statistics of the filter
	print("[I] Bloom Filter Statistic")
	print(
		"[+] Capacity: {} item(s)".format(line_count),
		"[+] Number of inserted items: {}".format(added),
		#"[+] Filter size: {} bit(s)".format(bf.filter_size),
		"[+] False Positive probability: {}".format(1e-16),
		#"[+] Number of hash functions: {}".format(bf.num_hashes),
		"[+] Input file: {}".format(file_txt),
		"[+] Output file: {}".format(file_bf),
		sep="\n",
		end="\n\n",
	)

	# Save to file
	print("[I] Bloom Filter Start Save File")
	bf.close()
	print("[I] Bloom Filter END Save File")

if __name__ == "__main__":

	if len (sys.argv) < 3:
		print ("Error. Too few parameters.")
		sys.exit (1)

	if len (sys.argv) > 3:
		print ("Error. Too many parameters.")
		sys.exit (1)

	file_txt = sys.argv[1]
	file_bf = sys.argv[2]

	line_count = count_lines(file_txt)
	print("all lines -> " + str(line_count))
	bloom_filter()
