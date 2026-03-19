#!/usr/bin/env python3
"""
file_cutter.py - Remove a slice of bytes from a file, keeping the rest.

Usage:
    python file_cutter.py <input_file> <position> <size> [output_file]

Arguments:
    input_file   Path to the source file
    position     Start offset of bytes to remove (supports 0x hex notation)
    size         Number of bytes to remove (supports 0x hex notation)
    output_file  (optional) Output file path. Defaults to <input_file>.cut
"""

import sys
import os


def parse_int(value: str) -> int:
    """Parse an integer from a string, supporting 0x hex notation."""
    return int(value, 0)


def cut_file(input_path: str, position: int, size: int, output_path: str) -> None:
    file_size = os.path.getsize(input_path)

    if position < 0:
        raise ValueError(f"Position must be >= 0, got {position}")
    if size <= 0:
        raise ValueError(f"Size must be > 0, got {size}")
    if position >= file_size:
        raise ValueError(
            f"Position {position} (0x{position:X}) is beyond end of file "
            f"({file_size} bytes)"
        )

    cut_end = position + size
    if cut_end > file_size:
        print(
            f"Warning: cut range ends at {cut_end} but file is only {file_size} bytes. "
            f"Clamping to end of file.",
            file=sys.stderr,
        )
        cut_end = file_size

    actual_removed = cut_end - position

    with open(input_path, "rb") as f_in:
        before = f_in.read(position)
        f_in.seek(cut_end)
        after = f_in.read()

    with open(output_path, "wb") as f_out:
        f_out.write(before)
        f_out.write(after)

    result_size = len(before) + len(after)
    print(
        f"Removed {actual_removed} byte(s) from '{input_path}' "
        f"at offset {position} (0x{position:X}) to {cut_end} (0x{cut_end:X})\n"
        f"Result: {file_size} -> {result_size} bytes\n"
        f"Output written to '{output_path}'"
    )


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    input_path = sys.argv[1]
    raw_position = sys.argv[2]
    raw_size = sys.argv[3]
    output_path = sys.argv[4] if len(sys.argv) >= 5 else input_path + ".cut"

    if not os.path.isfile(input_path):
        print(f"Error: input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        position = parse_int(raw_position)
        size = parse_int(raw_size)
    except ValueError as e:
        print(f"Error parsing position/size: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        cut_file(input_path, position, size, output_path)
    except (ValueError, OSError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
