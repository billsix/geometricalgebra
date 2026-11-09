#!/usr/bin/env bash
# Measure baseline Gn against the two frozendict variants (tasks/archive/2026/11/09/frozendict-research-and-fit.md).
# For each variant: the Gn micro-benchmark, the code generator's wall time (best of 3) with its
# g1-g3 output compared byte-for-byte to the baseline's, and the host `pytest -m "not slow"` wall
# time (best of 3) with its exit status.  Restores src/gacalc/gn.py to HEAD on exit.
# Run from anywhere; writes data/results.csv and data/*.log.  Takes about 15 minutes.
set -u
cd "$(git rev-parse --show-toplevel)"
A=tasks/adhoc/frozendict-research-and-fit
D=$A/data
mkdir -p "$D"
trap 'git checkout -q -- src/gacalc/gn.py' EXIT
echo "variant,measure,value" > "$D/results.csv"
best_of_3() {  # best wall seconds of three runs of "$@" -> $D/best; last run's exit -> $D/rc
    local best="" t s e rc
    for _ in 1 2 3; do
        s=$(date +%s.%N); "$@" > "$D/last.log" 2>&1; rc=$?; e=$(date +%s.%N)
        t=$(echo "$e - $s" | bc)
        if [ -z "$best" ] || [ "$(echo "$t < $best" | bc)" = 1 ]; then best=$t; fi
    done
    echo "$best" > "$D/best"; echo "$rc" > "$D/rc"
}
for v in baseline a b; do
    git checkout -q -- src/gacalc/gn.py
    case $v in
        baseline) ;;
        a) git apply "$A/variant-a-frozen-storage.patch" ;;
        b) git apply "$A/variant-b-frozen-storage-no-copy.patch" ;;
    esac
    PYTHONPATH=src python3 "$A/bench_gn.py" "$v" | sed 's/^\([^,]*\),\(.*\),\([^,]*\)$/\1,\2 (us),\3/' >> "$D/results.csv"
    best_of_3 env PYTHONPATH=src python3 tools/gen_specialized.py
    echo "$v,generator g1-g3 wall (s),$(cat "$D/best")" >> "$D/results.csv"
    mkdir -p "$D/gen-$v"; cp src/gacalc/g[123].py "$D/gen-$v/"
    same=identical
    for f in g1 g2 g3; do cmp -s "$D/gen-baseline/$f.py" "$D/gen-$v/$f.py" || same=DIFFERENT; done
    echo "$v,generator output vs baseline,$same" >> "$D/results.csv"
    best_of_3 env PYTHONPATH=src python3 -m pytest -q -m "not slow" -p no:cacheprovider
    echo "$v,pytest not-slow wall (s),$(cat "$D/best")" >> "$D/results.csv"
    echo "$v,pytest exit,$(cat "$D/rc")" >> "$D/results.csv"
    tail -1 "$D/last.log" > "$D/pytest-$v.log"
done
rm -rf "$D"/gen-a "$D"/gen-b "$D/last.log" "$D/best" "$D/rc"
cat "$D/results.csv"
