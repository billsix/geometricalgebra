#!/bin/env bash

# Activate the venv so ty/ruff resolve deps from it (the venv is
# --system-site-packages, so it also sees the dnf-installed base packages).
export VIRTUAL_ENV_DISABLE_PROMPT=1
[ -f /venv/bin/activate ] && source /venv/bin/activate

# The intentionally-vendored Emacs tree under entrypoint/ is excluded from both
# commands via `extend-exclude` in pyproject.toml [tool.ruff], so this formats the
# real project source without churning third-party files.
#
# Every step runs (one pass reports all the red), but the script exits nonzero
# if ANY step failed -- otherwise `make format` reports only the LAST command's
# status, and a `ty check` failure in an earlier step is silently masked (this
# actually happened: 3 ty errors sailed through a green gate, 2026-07-29).
status=0
ruff check . --fix || status=1
ruff format --line-length=88 || status=1

ty check src || status=1
ty check tests || status=1
ty check tools || status=1
exit $status
