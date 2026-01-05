#!/usr/bin/env bash

if [ $# -ne 1 ]; then
  echo "Usage: ./gen_hosts.sh x"
  exit 1
fi

x="$1"
out="hosts"

: > "$out"   # truncate/create file

for ((i=1; i<=x; i++)); do
  printf "%d localhost 11%03d\n" "$i" "$i" >> "$out"
done

echo "Generated $out with $x entries."
