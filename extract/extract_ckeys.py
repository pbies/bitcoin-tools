#!/usr/bin/env python3
"""
extract_ckeys.py — Extract ckey records from a Bitcoin Core wallet.dat file.

A 'ckey' (Crypted Key) is a Berkeley DB record in wallet.dat that stores
an AES-256-CBC encrypted private key alongside its public key.

Binary record structure (per Bitcoin Core walletdb.cpp):
┌─────────────────────────────────────────────────────────────────────┐
│  KEY FIELD (BDB record key)                                         │
│  [0x04] [0x63 0x6b 0x65 0x79]  — varint(4) + "ckey"               │
│  [0x21 or 0x41]                 — varint: pubkey length (33 or 65)  │
│  [33 or 65 bytes]               — compressed or uncompressed pubkey │
├─────────────────────────────────────────────────────────────────────┤
│  VALUE FIELD (BDB record value)                                     │
│  [0x30]                         — varint: 48                        │
│  [48 bytes]                     — AES-256-CBC encrypted privkey     │
└─────────────────────────────────────────────────────────────────────┘

Public key prefixes:
  0x02 / 0x03  → compressed   (33 bytes)
  0x04         → uncompressed (65 bytes)

Encrypted private key: always 48 bytes (32-byte key + 16-byte AES padding)

Usage:
    python extract_ckeys.py wallet.dat
    python extract_ckeys.py wallet.dat -o found_ckeys.txt -v
"""

import re
import sys
import argparse
from pathlib import Path


# ── Patterns ──────────────────────────────────────────────────────────────────

# After the "ckey" label comes a length-prefixed public key.
# Compressed pubkey:   0x21 (33) then 0x02 or 0x03 then 32 bytes
# Uncompressed pubkey: 0x41 (65) then 0x04 then 64 bytes
# Then 0x30 (varint 48) followed by 48 bytes of AES-256-CBC ciphertext.

PATTERN_COMPRESSED = re.compile(
    b"\x04ckey"           # "ckey" record marker (varint 4 + ASCII)
    b"\x21"               # varint: pubkey length = 33
    b"[\x02\x03]"         # compressed pubkey prefix
    b"[\x00-\xff]{32}"    # 32-byte X coordinate
    b"\x30"               # varint: encrypted privkey length = 48
    b"[\x00-\xff]{48}"    # 48-byte AES-256-CBC encrypted privkey
)

PATTERN_UNCOMPRESSED = re.compile(
    b"\x04ckey"           # "ckey" record marker
    b"\x41"               # varint: pubkey length = 65
    b"\x04"               # uncompressed pubkey prefix
    b"[\x00-\xff]{64}"    # 64-byte X+Y coordinates
    b"\x30"               # varint: encrypted privkey length = 48
    b"[\x00-\xff]{48}"    # 48-byte AES-256-CBC encrypted privkey
)


# ── Extraction ────────────────────────────────────────────────────────────────

def extract_ckeys(data: bytes) -> list:
    """
    Scan raw bytes for ckey records.
    Returns a list of dicts: offset, pubkey_type, pubkey_hex, enc_privkey_hex.
    """
    results = []

    for pattern, pubkey_len, key_type in [
        (PATTERN_COMPRESSED,   33, "compressed"),
        (PATTERN_UNCOMPRESSED, 65, "uncompressed"),
    ]:
        for m in pattern.finditer(data):
            raw    = m.group()
            offset = m.start()

            # Layout within the match:
            #   [0:4]                      b"\x04ckey"
            #   [4]                        pubkey length varint
            #   [5 : 5+pubkey_len]         full pubkey  (incl. prefix byte)
            #   [5+pubkey_len]             0x30 varint
            #   [5+pubkey_len+1 : +48]     encrypted privkey

            pubkey_start  = 5
            pubkey_end    = pubkey_start + pubkey_len
            enc_key_start = pubkey_end + 1   # skip the 0x30 varint byte
            enc_key_end   = enc_key_start + 48

            pubkey      = raw[pubkey_start:pubkey_end]
            enc_privkey = raw[enc_key_start:enc_key_end]

            results.append({
                "offset":          offset,
                "offset_hex":      f"0x{offset:08X}",
                "pubkey_type":     key_type,
                "pubkey_hex":      pubkey.hex(),
                "enc_privkey_hex": enc_privkey.hex(),
            })

    results.sort(key=lambda r: r["offset"])
    return results


# ── Output ────────────────────────────────────────────────────────────────────

def write_output(results: list, output_path: Path, source_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as f:
        f.write(f"# Bitcoin Core wallet.dat — ckey extraction\n")
        f.write(f"# Source : {source_path}\n")
        f.write(f"# Records: {len(results)}\n")
        f.write("#\n")
        f.write("# OFFSET      — file offset of the 'ckey' marker\n")
        f.write("# TYPE        — compressed (33 B) or uncompressed (65 B) pubkey\n")
        f.write("# PUBLIC KEY  — hex-encoded public key\n")
        f.write("# ENC PRIVKEY — hex-encoded AES-256-CBC encrypted private key (48 B)\n")
        f.write("#\n")
        f.write("=" * 80 + "\n\n")

        for i, rec in enumerate(results, 1):
            f.write(f"[ckey #{i}]\n")
            f.write(f"  Offset      : {rec['offset_hex']}  ({rec['offset']})\n")
            f.write(f"  Pubkey type : {rec['pubkey_type']}\n")
            f.write(f"  Public key  : {rec['pubkey_hex']}\n")
            f.write(f"  Enc privkey : {rec['enc_privkey_hex']}\n\n")

        if not results:
            f.write("No ckey records found.\n\n")
            f.write("Possible reasons:\n")
            f.write("  - Wallet is NOT encrypted (uses 'key' records, not 'ckey')\n")
            f.write("  - File is not a valid wallet.dat\n")
            f.write("  - Wallet uses the newer SQLite format (only BerkeleyDB supported)\n")


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract ckey (encrypted private key) records from a Bitcoin Core wallet.dat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("input",
                   help="Path to wallet.dat  (BerkeleyDB format)")
    p.add_argument("-o", "--output", default="ckeys_output.txt",
                   help="Output file  (default: ckeys_output.txt)")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Also print each record to stdout")
    return p.parse_args()


def main() -> None:
    args   = parse_args()
    in_path = Path(args.input)

    if not in_path.exists():
        sys.exit(f"[ERROR] File not found: {in_path}")

    size = in_path.stat().st_size
    print(f"[*] Reading  {in_path}  ({size:,} bytes) ...")
    data = in_path.read_bytes()

    # Quick sanity check — BerkeleyDB 4.x page magic
    BDB_MAGIC = b"\x00\x05\x31\x62"
    if BDB_MAGIC not in data[:4096]:
        print("[!] Warning: BerkeleyDB magic bytes not found.")
        print("    The file may not be a wallet.dat, or it may use the newer SQLite format.")
        print("    Continuing raw pattern scan anyway ...\n")

    print("[*] Scanning for ckey records ...")
    results = extract_ckeys(data)

    out_path = Path(args.output)
    write_output(results, out_path, in_path)

    print(f"[+] Found {len(results)} ckey record(s).")
    print(f"[+] Output written to: {out_path}")

    if args.verbose and results:
        print()
        for i, rec in enumerate(results, 1):
            print(f"  ckey #{i}  @{rec['offset_hex']}")
            print(f"    pubkey ({rec['pubkey_type']}): {rec['pubkey_hex']}")
            print(f"    enc privkey              : {rec['enc_privkey_hex']}")
            print()


if __name__ == "__main__":
    main()
