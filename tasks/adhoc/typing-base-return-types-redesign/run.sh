#!/usr/bin/env bash
# Type-check the toy typing model: design.py must be clean, and design_neg.py must
# report exactly its three deliberate misuses. Run from anywhere.
cd "$(dirname "$0")" || exit 1
status=0
ty check design.py || status=1
neg_count=$(ty check design_neg.py --output-format concise 2>&1 | grep -c "error\[")
if [ "$neg_count" -ne 3 ]; then
  echo "design_neg.py: expected 3 errors, got $neg_count"; status=1
else
  echo "design_neg.py: the 3 misuses are rejected"
fi
exit $status
