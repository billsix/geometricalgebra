#!/usr/bin/env bash
# List test-function families that differ only by a variant token (2d/3d, gn/g2/g3,
# 1d..5d), per file: strip the token from each name and print names that collide.
# Run from anywhere; writes data/families.txt next to this script.
cd "$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)" || exit 1
out="tasks/adhoc/tests-parametrize-variants-and-dimensions/data/families.txt"
git grep -n -E '^def test_' -- 'tests/*.py' |
  sed -E 's/^([^:]+):([0-9]+):def (test_[A-Za-z0-9_]+).*/\1 \3/' |
  awk '{ key = $2; gsub(/_(1d|2d|3d|4d|5d|gn|g1|g2|g3|g4|g5)(_|$)/, "_", key); sub(/_$/, "", key);
         print $1, key, $2 }' |
  sort -k1,1 -k2,2 |
  awk '{ k = $1 " " $2; names[k] = names[k] " " $3; n[k]++ }
       END { for (k in n) if (n[k] > 1) print k ":" names[k] }' |
  sort > "$out"
wc -l < "$out"
