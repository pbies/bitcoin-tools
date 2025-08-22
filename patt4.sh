#!/usr/bin/env bash

# works!

find plain -type f -name "*.txt" -exec sh -c '
	for file do
		echo "===> Szukam w: $file" >&2
		grep -nH -f patt2.txt "$file"
	done
' sh {} + > results4.txt

# no progress
