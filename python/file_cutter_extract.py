#!/usr/bin/env python3
"""
file_cutter.py - Extract a slice of bytes from a file.

Usage:
    python file_cutter.py <input_file> <position> <size> [output_file]

Arguments:
    input_file   Path to the source file
    position     Start offset in bytes (supports 0x hex notation)
    size         Number of bytes to extract (supports 0x hex notation)
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

    available = file_size - position
    if size > available:
        print(
            f"Warning: requested {size} bytes but only {available} available "
            f"from position {position}. Truncating.",
            file=sys.stderr,
        )
        size = available

    with open(input_path, "rb") as f_in:
        f_in.seek(position)
        data = f_in.read(size)

    with open(output_path, "wb") as f_out:
        f_out.write(data)

    print(
        f"Cut {len(data)} byte(s) from '{input_path}' "
        f"at offset {position} (0x{position:X})\n"
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
