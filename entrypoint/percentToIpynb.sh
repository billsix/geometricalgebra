#!/usr/bin/env bash
# Convert jupytext percent-format notebooks to .ipynb, written beside each source.
# Arguments are file names in notebooks/ (e.g. displaymv.py); with none, every
# notebooks/*.py is converted. Run by `make notebooks-ipynb [NOTEBOOKS='...']`.
set -e
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate
cd /gacalc/notebooks
if [ "$#" -eq 0 ]; then
    set -- *.py
fi
jupytext --to ipynb "$@"
