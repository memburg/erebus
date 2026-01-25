#!/usr/bin/env bash
set -euo pipefail

# Run Erebus N times and report the average wall-clock time.

usage() {
  echo "Usage: $0 [-r runs] -i IMAGE -s SEED -n ITERATIONS" >&2
  echo "       $0 [-r runs] IMAGE ITERATIONS SEED" >&2
  exit 1
}

image=""
seed=""
iterations=""
runs=10

while getopts ":i:s:n:r:h" opt; do
  case "$opt" in
    i) image=$OPTARG ;;
    s) seed=$OPTARG ;;
    n) iterations=$OPTARG ;;
    r) runs=$OPTARG ;;
    h) usage ;;
    *) usage ;;
  esac
done
shift $((OPTIND-1))

# Fallback: accept positional IMAGE ITERATIONS SEED
if [[ -z "$image" && $# -ge 3 ]]; then
  image=$1
  iterations=$2
  seed=$3
fi

[[ -n "$image" && -n "$seed" && -n "$iterations" ]] || usage
[[ -f "$image" ]] || { echo "Image not found: $image" >&2; exit 1; }
[[ "$runs" =~ ^[0-9]+$ && "$runs" -gt 0 ]] || { echo "Invalid runs: $runs" >&2; exit 1; }
[[ "$seed" =~ ^-?[0-9]+$ ]] || { echo "Invalid seed: $seed" >&2; exit 1; }
[[ "$iterations" =~ ^[0-9]+$ && "$iterations" -gt 0 ]] || { echo "Invalid iterations: $iterations" >&2; exit 1; }

cmd=(python3 src/erebus.py "$image" "$seed" "$iterations")

echo "Benchmarking: ${cmd[*]}"
echo "Runs: $runs"
echo

times=()
TIMEFORMAT=%R

for ((i=1; i<=runs; i++)); do
  t=$( { time "${cmd[@]}" >/dev/null; } 2>&1 )
  times+=("$t")
  printf "Run %2d: %s s\n" "$i" "$t"
done

avg=$(printf '%s\n' "${times[@]}" | awk '{sum+=$1} END{if (NR>0) printf "%.6f", sum/NR; else print "nan"}')

echo
echo "Average: $avg s"
