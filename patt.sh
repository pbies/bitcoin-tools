#!/usr/bin/env bash
grep -r --include="*.txt" -n -H -f patt.txt . > results
