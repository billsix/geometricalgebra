#!/bin/bash
# Nest one-caller helpers in each given script with the shared nest_one_caller.py.
# Notebooks and figure scripts are run (jupytext, exec), never imported, so a
# same-named helper in another file is not a second caller; each file is nested
# alone in a scratch repository, where the tool's cross-file check has nothing to
# match. Usage: nest_isolated.sh FILE... (repository-relative); edits in place.
set -u
root="$(git rev-parse --show-toplevel)"
for rel in "$@"; do
    scratch="$(mktemp -d)"
    cp "$root/$rel" "$scratch/"
    (
        cd "$scratch" || exit 1
        git init -q
        git add .
        python3 ~/.claude/reference/nest_one_caller.py "$(basename "$rel")"
    ) | grep -E "^  (nest|skip)" | sed "s|^|$rel: |"
    cp "$scratch/$(basename "$rel")" "$root/$rel"
    rm -rf "$scratch"
done
