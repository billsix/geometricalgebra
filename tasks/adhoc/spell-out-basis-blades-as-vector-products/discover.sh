#!/usr/bin/env bash
# List every line of the book, its figures and the notebooks that names a basis blade of
# grade 2 or 3 by its compound index (e_12, \mathbf{e}_{12}, e₁₂, e_{ij}, ...), as
# file:line:text. Run from anywhere; writes data/matches.txt next to this script.
#
# The worklog is a snapshot: match on content when fixing, not on the saved line numbers.

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(git -C "$here" rev-parse --show-toplevel)" || exit 1

pattern='(e\}?_\{?(12|13|23|21|31|32|123|ij)\}?([^0-9]|$))|e₁₂|e₁₃|e₂₃|e₁₂₃|\be(12|13|23|31|123)\b'

mkdir -p "$here/data"
git grep -n -E "$pattern" -- 'book/docs/*.rst' 'book/figures' 'notebooks/*.py' \
    > "$here/data/matches.txt"
status=$?

wc -l < "$here/data/matches.txt"
exit "$status"
