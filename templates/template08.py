#!/usr/bin/env python3

import sys, os, datetime, time, argparse, json
from pathlib import Path
from functools import wraps

start_msg = ''
start_time = 0

def timer(func):
	"""Decorator to time function execution."""
	@wraps(func)
	def wrapper(*args, **kwargs):
		func_start = time.time()
		result = func(*args, **kwargs)
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

@timer
def load_config(config_path):
	"""Load configuration from JSON file."""
	if config_path and Path(config_path).exists():
		with open(config_path) as f:
			return json.load(f)
	return {}

def main():
	os.system('cls' if os.name == 'nt' else 'clear')
	print(f'{__file__} = {sys.argv[0]}')
	global start_msg, start_time
	start_msg = 'Program started: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(start_msg)
	start_time = time.time()

	args = parse_args()
	config = load_config(args.config)

	if args.verbose:
		log_step('Verbose mode enabled')
		if config:
			log_step(f'Loaded config: {json.dumps(config)}')

	# your code here

	stop_time = time.time()
	print(start_msg)
	print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	print(f'Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}')
	print('\a', end='', file=sys.stderr)

# https://stackoverflow.com/questions/5925918/python-suppressing-errors-from-going-to-commandline
class SuppressErrors:
	def write(self, *args):
		pass
	def flush(self, *args):
		pass

if __name__ == '__main__':
	sys.tracebacklimit = 0
	sys.stderr = SuppressErrors()
	try:
		main()
	except KeyboardInterrupt:
		stop_time = time.time()
		print('\nKeyboard break!\a')
		print(start_msg)
		print('Program stopped: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
		print(f'Execution took: {str(datetime.timedelta(seconds=stop_time - start_time))}')
		try:
			sys.exit(130)
		except SystemExit:
			os._exit(130)
