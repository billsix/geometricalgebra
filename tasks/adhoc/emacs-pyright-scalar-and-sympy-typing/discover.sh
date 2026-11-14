#!/usr/bin/env bash
# Run pyright (the version Emacs uses) over src, tests and both notebook trees in the
# gacalc image, write its JSON report to data/pyright.json, then list the errors whose
# cause is a sympy Expr where a multivector is expected in data/expr-sites.tsv.
# Run from anywhere; needs the gacalc image (make image).
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo="$(git -C "$here" rev-parse --show-toplevel)"
mkdir -p "$here/data"
podman run ${PODMAN_RUN_FLAGS:-} --rm --entrypoint /bin/bash \
  -v "$repo":/gacalc/:Z gacalc \
  -c 'source /venv/bin/activate; cd /gacalc; python tools/gen_specialized.py >/dev/null;
      pyright --outputjson src/gacalc tests notebooks book/docs/notebooks' \
  > "$here/data/pyright.json"
python3 "$here/extract.py" "$here/data/pyright.json" > "$here/data/expr-sites.tsv"
wc -l < "$here/data/expr-sites.tsv"
# The committed snapshots are data/expr-sites-before.tsv (the 166 sites the codemod
# and the hand edits worked from) and data/expr-sites-after.tsv (the 3 left).
