#!/usr/bin/env python3

import sys
import os
import json
import base64


def b64_validate(value: str) -> str:
	value = value.strip()
	base64.b64decode(value, validate=True)
	return value


def parse_metamask_hashcat_line(line: str):
	"""
	Accepts MetaMask hashes in these formats:

	26600:
		$metamask$<b64_salt>$<b64_iv>$<b64_data>

	16300:
		$metamask$<iterations>$<b64_salt>$<b64_iv>$<b64_data>

	Returns (obj, "ok") or (None, reason).
	"""
	line = line.strip()
	if not line or line.startswith("#"):
		return None, "empty/comment"

	if not line.startswith("$metamask$"):
		return None, "not metamask hash"

	parts = line.split("$")
	# Examples:
	# 26600 => ["", "metamask", salt, iv, data]            len=5
	# 16300 => ["", "metamask", iters, salt, iv, data]     len=6
	if len(parts) not in (5, 6):
		return None, f"bad token count: {len(parts)}"

	if parts[1] != "metamask":
		return None, "bad tag"

	try:
		if len(parts) == 5:
			salt, iv, data = parts[2], parts[3], parts[4]
			iterations = None
		else:
			iterations_str, salt, iv, data = parts[2], parts[3], parts[4], parts[5]
			if not iterations_str.isdigit():
				return None, "iterations not numeric"
			iterations = int(iterations_str, 10)

		salt = b64_validate(salt)
		iv = b64_validate(iv)
		data = b64_validate(data)

	except Exception as e:
		return None, f"invalid base64: {e}"

	obj = {
		"data": data,
		"iv": iv,
		"salt": salt
	}
	if iterations is not None:
		obj["keyMetadata"] = {
			"algorithm": "PBKDF2",
			"params": {
				"iterations": iterations
			}
		}

	return obj, "ok"


def convert_file(input_file: str, output_file: str, fmt: str):
	ok = []
	fail = []

	with open(input_file, "r", encoding="utf-8", errors="replace") as f:
		for line_no, raw in enumerate(f, 1):
			line = raw.strip()
			if not line or line.startswith("#"):
				continue

			obj, err = parse_metamask_hashcat_line(line)
			if obj:
				ok.append(obj)
			else:
				fail.append((line_no, err))

	if fmt == "jsonl":
		with open(output_file, "w", encoding="utf-8") as f:
			for obj in ok:
				f.write(json.dumps(obj, ensure_ascii=False) + "\n")
	else:
		with open(output_file, "w", encoding="utf-8") as f:
			json.dump(ok, f, ensure_ascii=False, indent=2)
			f.write("\n")

	print(f"input: {input_file}")
	print(f"output: {output_file}")
	print(f"ok: {len(ok)}")
	print(f"fail: {len(fail)}")
	if fail:
		for line_no, err in fail[:10]:
			print(f"fail[{line_no}]: {err}")
		if len(fail) > 10:
			print(f"... and {len(fail) - 10} more")


def main():
	if len(sys.argv) < 2:
		print(f"usage: {sys.argv[0]} hashes.txt [out.json|out.jsonl] [json|jsonl]")
		sys.exit(1)

	inp = sys.argv[1]
	if not os.path.exists(inp):
		print(f"error: input file not found: {inp}")
		sys.exit(1)

	out = sys.argv[2] if len(sys.argv) >= 3 else os.path.splitext(inp)[0] + "_wallets.jsonl"

	if len(sys.argv) >= 4:
		fmt = sys.argv[3].strip().lower()
	else:
		fmt = "jsonl" if out.lower().endswith(".jsonl") else "json"

	if fmt not in ("json", "jsonl"):
		print("error: format must be json or jsonl")
		sys.exit(1)

	convert_file(inp, out, fmt)


if __name__ == "__main__":
	main()
