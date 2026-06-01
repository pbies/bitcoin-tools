#!/usr/bin/env python3
import os
import sys
import numpy as np
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

sys.stdout.reconfigure(encoding='ascii', errors='replace')

OUTPUT    = 'output.txt'
TOTAL     = 2**32
LINE_SIZE = 9          # '00000000\n'
CHUNK     = 1 << 23   # 8 M lines ~ 72 MB per worker slot

# two-hex-digit lookup: index=byte value -> two ASCII bytes
_HEX = np.frombuffer(
    b''.join(f'{i:02x}'.encode() for i in range(256)),
    dtype=np.uint8,
).reshape(256, 2).copy()


def write_chunk(args):
    path, start, end = args
    arr = np.arange(start, end, dtype=np.uint32)

    buf = np.empty((end - start, LINE_SIZE), dtype=np.uint8)
    buf[:, 0:2] = _HEX[(arr >> 24).astype(np.uint8)]
    buf[:, 2:4] = _HEX[(arr >> 16).astype(np.uint8)]
    buf[:, 4:6] = _HEX[(arr >>  8).astype(np.uint8)]
    buf[:, 6:8] = _HEX[ arr       .astype(np.uint8)]
    buf[:, 8]   = 0x0a  # '\n'

    raw = buf.tobytes()
    flags = os.O_WRONLY | getattr(os, 'O_BINARY', 0)
    fd = os.open(path, flags)
    try:
        os.lseek(fd, start * LINE_SIZE, os.SEEK_SET)
        mv, pos = memoryview(raw), 0
        while pos < len(raw):
            pos += os.write(fd, mv[pos : pos + 64 << 20])
    finally:
        os.close(fd)


def main():
    print('Allocating...')
    with open(OUTPUT, 'wb') as f:
        f.seek(TOTAL * LINE_SIZE - 1)
        f.write(b'\x00')

    chunks = [
        (OUTPUT, s, min(s + CHUNK, TOTAL))
        for s in range(0, TOTAL, CHUNK)
    ]

    print('Writing...')
    with Pool(cpu_count()) as pool:
        list(tqdm(pool.imap_unordered(write_chunk, chunks), total=len(chunks)))

    print('Done.\a')


if __name__ == '__main__':
    main()
