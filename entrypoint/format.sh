#!/bin/env bash

# Activate the venv so ty/ruff resolve deps from it (the venv is
# --system-site-packages, so it also sees the dnf-installed base packages).
export VIRTUAL_ENV_DISABLE_PROMPT=1
source /venv/bin/activate

# The intentionally-vendored Emacs tree under entrypoint/ is excluded from both
# commands via `extend-exclude` in pyproject.toml [tool.ruff], so this formats the
# real project source without churning third-party files.
ruff check . --fix
ruff format --line-length=88

ty check /gacalc/src
ty check /gacalc/tests
