#!/usr/bin/env python3

import sys, os, datetime, time, argparse, json
from pathlib import Path
from functools import wraps

_start_msg = ''
_start_time = 0.0

def timer(func, verbose_flag=None):
	"""Decorator to time function execution. Only prints if verbose is True."""
	@wraps(func)
	def wrapper(*args, **kwargs):
		func_start = time.time()
		result = func(*args, **kwargs)
		if verbose_flag is None or (isinstance(verbose_flag, list) and verbose_flag[0]):
			func_elapsed = time.time() - func_start
			print(f'  [{func.__name__}] took {func_elapsed:.4f}s')
		return result
	return wrapper

def log_step(message):
	"""Print a timestamped step message."""
	timestamp = datetime.datetime.now().strftime('%H:%M:%S')
	print(f'[{timestamp}] {message}')

def parse_args():
	parser = argparse.ArgumentParser(description='Extended template script')
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
	parser.add_argument('-c', '--config', type=str, help='Path to config JSON file')
	parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')
	return parser.parse_args()

def load_config(config_path, verbose=False):
	"""Load configuration from JSON file."""
	if not config_path:
		return {}
	p = Path(config_path)
	if not p.exists():
		print(f'Warning: config file not found: {config_path}')
		return {}
	t0 = time.time()
	with open(p) as f:
		data = json.load(f)
	if verbose:
		print(f'  [load_config] took {time.time() - t0:.4f}s')
	return data

def format_elapsed(seconds):
	"""Format elapsed seconds as H:MM:SS.mmm"""
	h = int(seconds // 3600)
	m = int((seconds % 3600) // 60)
	s = seconds % 60
	return f'{h}:{m:02d}:{s:06.3f}'

def print_summary(start_msg, start_time):
	stop_time = time.time()
	print(start_msg)
	print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {format_elapsed(stop_time - start_time)}')
	sys.stdout.write('\a')
	sys.stdout.flush()

def clear_screen():
	sys.stdout.write('\033[2J\033[H')
	sys.stdout.flush()

def main():
	global _start_msg, _start_time
	clear_screen()
	print(f'{__file__} = {sys.argv[0]}')
	_start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(_start_msg)
	_start_time = time.time()

	args = parse_args()
	config = load_config(args.config, verbose=args.verbose)

	if args.verbose:
		log_step('Verbose mode enabled')
		if config:
			log_step(f'Loaded config: {json.dumps(config)}')

	# your code here

	print_summary(_start_msg, _start_time)

if __name__ == '__main__':
	sys.tracebacklimit = 0
	_start_time = time.time()
	_start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	try:
		main()
	except KeyboardInterrupt:
		print('\nKeyboard break!')
		print_summary(_start_msg, _start_time)
		os._exit(130)
