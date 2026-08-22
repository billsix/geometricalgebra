export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
cd /gacalc/
# The specialized algebras (scalar/g1/g2/g3.py) are generated, not tracked in
# git -- produce them into the (bind-mounted) tree before the editable install
# and before the user gets a prompt, so tests/IDE/ty/ruff all see real files.
# Only the dev-default dims (g1--g3) are built here; g4/g5 are release-only (they
# take ~5 min / ~87 min) and are generated with GACALC_DIMS in make dist/release.
# The default is set explicitly rather than relying on the generator's built-in
# GACALC_DIMS default, mirroring make dist's GACALC_DIMS=1,2,3,4,5.
DEV_DIMS=1,2,3
GACALC_DIMS=$DEV_DIMS python tools/gen_specialized.py
uv pip install --python $(which python) --no-deps --no-index --no-build-isolation -e .
exec bash
