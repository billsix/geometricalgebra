#!/usr/bin/env bash
# Snapshot every annotation-auditor row, for tasks/re-baseline-annotation-auditor-after-gl-move.md.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
python tools/check_annotations.py --full >tasks/adhoc/re-baseline-annotation-auditor-after-gl-move/data/rows-before.txt
tail -3 tasks/adhoc/re-baseline-annotation-auditor-after-gl-move/data/rows-before.txt
