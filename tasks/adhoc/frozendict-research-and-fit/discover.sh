#!/usr/bin/env bash
# Discovery for tasks/frozendict-research-and-fit.md phase 2: every dict-typed
# annotation, BladeReal use, Gn storage access and module-level dict constant in
# the hand-written source.  Run from the repo root; writes data/*.txt.
set -u
cd "$(git rev-parse --show-toplevel)"
out=tasks/adhoc/frozendict-research-and-fit/data
git grep -n -E "dict\[" -- src tools ':!src/gacalc/g[0-9].py' > "$out/dict-annotations.txt"
git grep -n "BladeReal" -- src tools tests notebooks book/docs/notebooks ':!src/gacalc/g[0-9].py' > "$out/bladereal-uses.txt"
git grep -n "coefficient_of_blade" -- src tools tests notebooks book/docs/notebooks ':!src/gacalc/g[0-9].py' > "$out/coefficient-of-blade.txt"
git grep -n -E "^[A-Z_][A-Z0-9_]*(: [^=]+)? = \{" -- src tools > "$out/module-dict-constants.txt"
wc -l "$out"/*.txt
