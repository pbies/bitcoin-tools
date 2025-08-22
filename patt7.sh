#!/usr/bin/env bash

# works!

set -euo pipefail

OUT="results7.txt"
PAT="patt2.txt"

find plain -type f -name '*.txt' ! -name "$OUT" -print0 |
xargs -0 -I{} sh -c '
	printf "===> Szukam w: %s\n" "$1" >&2
	grep -nH -f "'"$PAT"'" "$1"
' _ {} > "$OUT"
