#!/usr/bin/env bash
# Discovery for the Coef→Real / from_scalar+from_coef→from_real rename: every tracked site of the
# four names, logged to data/sites.txt. Run from anywhere; paths are repo-relative.
cd "$(git rev-parse --show-toplevel)" || exit 1
git grep -nwE 'Coef|BladeCoef|from_scalar|from_coef' -- src tools tests notebooks README.md book CLAUDE.md tasks/reference \
  ':!tasks/reference/scalar-vs-real-naming.md' > tasks/adhoc/consider-renaming-scalar-to-real/data/sites.txt
wc -l tasks/adhoc/consider-renaming-scalar-to-real/data/sites.txt
