#!/usr/bin/env bash
# Discovery for tasks/coordinate-subscripts-indices-not-xyz: every axis-letter coordinate
# subscript (`a_x`, `\vec{b}'_y`, `b_z`, ...) in the book's prose, companion notebooks, ePiX
# figure labels, and the outline doc that quotes the book. Run from anywhere; prints
# `file:line:text` and exits 0 even with no hits (re-run after the fix: zero lines = done).
#
#   tasks/adhoc/coordinate-subscripts-indices-not-xyz/discover.sh > .../data/hits-before.txt
set -u
cd "$(git rev-parse --show-toplevel)"
grep -nE '\\vec\{[a-z]\}'"'"'?_\{?[xyz]\}?|\b[a-z]'"'"'?_[xyz]\b' \
  book/docs/*.rst book/docs/notebooks/*.py book/figures/epix/*.py \
  tasks/reference/book-outline.md
exit 0
