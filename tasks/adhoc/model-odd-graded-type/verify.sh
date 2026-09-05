# Ad-hoc verification harness for the Odd_3 graded type (tasks/model-odd-graded-type.md).
#
# Regenerates the specialized modules, then runs the checks the DEV gate cannot: it skips
# the gitignored generated g*.py, so a plain `make format` never type-checks Odd_3's
# generated code.  This runs, in order:
#   1. the generator (writes g1/g2/g3.py into the working tree);
#   2. the doc-region marker check (the new to_vector/to_trivector regions must stay unique);
#   3. a FULL-CONTEXT ty check -- every generated module passed together with base/functions/
#      transforms (a single-file `ty check g3.py` gives false isolation errors, so all at once);
#   4. the full test suite.
#
# Run from the repo root inside the container:
#     make shell-exec SCRIPT=tasks/adhoc/model-odd-graded-type/verify.sh
set -e
GACALC_DIMS=1,2,3 python tools/gen_specialized.py 2>&1 | tail -1
echo "=== doc-regions ==="
python tools/check_doc_regions.py 2>&1 | tail -2
echo "=== ty (full context, incl. generated g1/g2/g3 with Odd_3 + casts) ==="
ty check src/gacalc/g1.py src/gacalc/g2.py src/gacalc/g3.py src/gacalc/gn.py \
         src/gacalc/base.py src/gacalc/functions.py src/gacalc/transforms.py 2>&1 | tail -4
echo "=== pytest ==="
python -m pytest -q 2>&1 | tail -4
