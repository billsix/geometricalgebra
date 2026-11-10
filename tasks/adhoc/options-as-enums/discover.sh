#!/usr/bin/env bash
# Discover string-valued option parameters (options-as-enums task).
# Run from anywhere; paths are repo-root relative.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
rg -n --glob '!src/gacalc/g[1-5].py' --glob '!*#*' \
  -e 'Literal\[' \
  -e ': str( \| None)? = "' \
  -e 'case "[a-z_]+"' \
  -e '(==|!=|in) \(?"[a-z_]+"' \
  src tools notebooks book/docs/notebooks
