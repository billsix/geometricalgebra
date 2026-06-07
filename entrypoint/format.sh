#!/bin/env bash

# The intentionally-vendored Emacs tree under entrypoint/ is excluded from both
# commands via `extend-exclude` in pyproject.toml [tool.ruff], so this formats the
# real project source without churning third-party files.
ruff check . --fix
ruff format --line-length=88

ty check /gacalc/src
ty check /gacalc/tests
