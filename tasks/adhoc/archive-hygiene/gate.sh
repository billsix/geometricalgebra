#!/usr/bin/env bash
# The archive-hygiene gate: re-run discover.sh into a scratch dir and fail on any hit that is
# not an accepted exception.
#   - scaffolding.txt, bill.txt, container-paths.txt must be empty;
#   - each missing-paths.txt hit must be attributed to another repo (a github.com/ URL on the
#     same line or the line above, where the citation wrapped) or say "no longer exists";
#   - dead-shas.txt hits are printed for review: each must be labelled in its sentence as
#     another repo's commit, a doc-region hash or an image ID.
set -u
root=$(git rev-parse --show-toplevel)
cd "$root" || exit 1
out=$(mktemp -d)
bash tasks/adhoc/archive-hygiene/discover.sh "$out" > /dev/null
status=0
for f in scaffolding bill container-paths; do
  if [ -s "$out/$f.txt" ]; then
    echo "FAIL $f:"; cat "$out/$f.txt"; status=1
  else
    echo "ok   $f: none"
  fi
done
bad=0
while IFS=: read -r file line path; do
  prev=$((line > 1 ? line - 1 : 1))
  if sed -n "${prev},${line}p" "$file" | grep -qE 'github\.com/|no longer exists'; then
    continue
  fi
  echo "FAIL unattributed missing path $file:$line:$path"; bad=1
done < "$out/missing-paths.txt"
[ "$bad" = 0 ] && echo "ok   missing paths: $(wc -l < "$out/missing-paths.txt") hits, all other-repo or marked gone"
[ "$bad" = 0 ] || status=1
echo "review dead-shas (must be labelled other-repo / doc-region / image ID):"
cut -d: -f1,3 "$out/dead-shas.txt" | sort -u | sed 's/^/     /'
rm -rf "$out"
exit $status
