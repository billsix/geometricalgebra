#!/usr/bin/env bash
# List every cancellation display in the notebooks (a show_difference or show_cancellation
# call, not the import line) as file:line:text. Run from anywhere; writes data/calls.txt
# next to this script.
#
# The worklog is a snapshot: match on the call's text when pruning, not on the line number.

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(git -C "$here" rev-parse --show-toplevel)" || exit 1

mkdir -p "$here/data"
git grep -n -E '^ *show_(difference|cancellation)\(' -- 'notebooks/*.py' \
    > "$here/data/calls.txt"
status=$?

wc -l < "$here/data/calls.txt"
exit "$status"
