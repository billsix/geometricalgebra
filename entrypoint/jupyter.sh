#!/usr/bin/env bash
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
cd /gacalc
# The specialized algebras (g1/g2/g3.py) are generated, not tracked in
# git -- produce them and install editable so the notebooks can import gacalc
# against the live source, whether launched via `make jupyter` or from a shell
# (mirrors shell.sh).
python tools/gen_specialized.py
uv pip install --python $(which python) --no-deps --no-index --no-build-isolation -e .
# in general this is super dangerous, but for our purposes,
# it's fine
# JupyterLab opens in notebooks/, where every notebook lives (notebooks/README.md lists
# them); the rest of the repository stays browsable. Every notebook asks for the venv's
# python3 kernel, which imports the editable gacalc installed above.
exec jupyter lab \
         --allow-root \
         --ip=0.0.0.0 \
         --port=8888 \
         --ServerApp.token='' \
         --ServerApp.password='' \
         --ServerApp.disable_check_xsrf=True \
         --LabApp.default_url=/lab/tree/notebooks \
         --no-browser \
         --MultiKernelManager.default_kernel_name=python3
