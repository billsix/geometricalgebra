#!/usr/bin/env bash
# Inventory how gacalc chooses float vs symbolic behaviour, for
# tasks/reference/numeric-symbolic-mode.md. Run from anywhere; writes data/.
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1
out=tasks/adhoc/research-numeric-symbolic-mode-threading/data
git grep -n "float_close_to_zero" -- "*.py" ":!src/gacalc/g[0-9].py" >"$out/float_close_to_zero.txt"
git grep -n "MatrixBackend\|backend=" -- "*.py" ":!src/gacalc/g[0-9].py" >"$out/matrix_backend.txt"
git grep -n -E "isinstance\([^)]*float|_has_float|is_float|\.is_Float" -- "*.py" ":!src/gacalc/g[0-9].py" >"$out/type_dispatch.txt"
git grep -n -E "^_[a-z_]+: .*= |ContextVar|global " -- "src/gacalc/*.py" ":!src/gacalc/g[0-9].py" >"$out/module_state.txt"
wc -l "$out"/*.txt
