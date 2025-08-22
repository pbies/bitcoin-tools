#!/usr/bin/env bash

# works!

set -euo pipefail

OUT="results5.txt"
PAT="patt2.txt"

# przeszukuj tylko .txt, ale pomiń plik wynikowy
find plain -type f -name '*.txt' ! -name "$OUT" -exec sh -c '
	pat="$1"; shift
	for file do
		printf "===> Szukam w: %s\n" "$file" >&2
		grep -nH -f "$pat" "$file"
	done
' sh "$PAT" {} \; >"$OUT"
