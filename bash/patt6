#!/usr/bin/env bash

# works!

set -euo pipefail

OUT="results6.txt"
PAT="patt2.txt"

find plain -type f -name '*.txt' ! -name "$OUT" -exec sh -c '
	pat="$1"; shift
	for file do
		printf "===> Szukam w: %s\n" "$file" >&2
		grep -nH -f "$pat" "$file"
	done
' sh "$PAT" {} + >"$OUT"
