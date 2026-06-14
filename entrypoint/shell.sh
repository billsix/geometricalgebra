export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
cd /gacalc/
# The specialized algebras (scalar/g1/g2/g3.py) are generated, not tracked in
# git -- produce them into the (bind-mounted) tree before the editable install
# and before the user gets a prompt, so tests/IDE/ty/ruff all see real files.
python tools/gen_specialized.py
uv pip install --python $(which python) --no-deps --no-index --no-build-isolation -e .
exec bash
