#!/usr/bin/env bash
# The discovery greps behind the cancellation sweep: every place the book says or
# checks that something cancels, in the index (run before staging the sweep, it is the
# pre-sweep snapshot). Run from the repo root; writes data/discover.txt.
out=tasks/adhoc/cancellation-underbrace-everywhere/data/discover.txt
status=0
{
  echo "== prose and markdown mentioning cancel"
  git grep --cached -n -i -E "cancel" -- "notebooks/*.py" "book/docs/*.rst" || status=1
  echo "== notebook cells after a 'difference' markdown cell"
  git grep --cached -n -i -E "^# .*difference" -- "notebooks/*.py" || status=1
  echo "== simplify / zero checks in notebook code"
  git grep --cached -n -E "simplify|== 0|\.expand\(" -- "notebooks/*.py" | grep -v ":#" || status=1
} > "$out"
exit $status
