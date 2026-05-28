#!/usr/bin/env python3

import sys
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import threading

sys.stdout.reconfigure(encoding='ascii', errors='replace')

WORKERS = os.cpu_count() - 2
_lock = threading.Lock()

SECP256K1_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
HEX64_RE = re.compile(r'^[0-9a-fA-F]{64}$')

def validate(k):
    s = k.strip()
    if not HEX64_RE.match(s):
        return s, False
    val = int(s, 16)
    return s, 1 <= val < SECP256K1_ORDER

def main():
    with open('input.txt', 'r') as f:
        print('Reading...', flush=True)
        lines = f.read().splitlines()

    good_buf = []
    bad_buf = []
    FLUSH_EVERY = 1000

    def flush(good_f, bad_f, force=False):
        if force or len(good_buf) >= FLUSH_EVERY:
            good_f.write('\n'.join(good_buf) + ('\n' if good_buf else ''))
            good_f.flush()
            good_buf.clear()
        if force or len(bad_buf) >= FLUSH_EVERY:
            bad_f.write('\n'.join(bad_buf) + ('\n' if bad_buf else ''))
            bad_f.flush()
            bad_buf.clear()

    print(f'Validating with {WORKERS} threads...', flush=True)

    with open('output-good.txt', 'w') as good_f, open('output-bad.txt', 'w') as bad_f:
        with ThreadPoolExecutor(max_workers=WORKERS) as executor:
            futures = {executor.submit(validate, k): k for k in lines}
            with tqdm(total=len(lines)) as bar:
                for future in as_completed(futures):
                    k, ok = future.result()
                    with _lock:
                        if ok:
                            good_buf.append(k)
                        else:
                            bad_buf.append(k)
                        flush(good_f, bad_f)
                    bar.update(1)
        with _lock:
            flush(good_f, bad_f, force=True)

    print('\a', end='', file=sys.stderr)

if __name__ == '__main__':
    main()
