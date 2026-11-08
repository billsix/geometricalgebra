# Anchor the `.dockerignore` cache patterns with `**/`

Done 2026-11-08 (William Emerison Six <billsix@gmail.com> asked for it), on branch
`dockerignore-anchor-patterns`.

## What changed

`.dockerignore` patterns are anchored at the context root, unlike `.gitignore`, so `__pycache__/`,
`*.py[cod]`, `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/` and `.ipynb_checkpoints/` excluded only
top-level matches. They are now `**/`-prefixed, with a comment saying why. `build/` and `dist/` stay
root-only. Found while adding `.dockerignore` to github.com/billsix/methodfinder; the rule is in the
Dockerfile contract's `.dockerignore` bullet (personal overlay, github.com/billsix/dotfiles
`.ai-coding-conventions.personal.md`).

## Verification (2026-11-08, nested podman)

A probe build with this repo as context (`FROM fedora:45`, `COPY entrypoint/dotfiles/`, `COPY src`,
`COPY tools`, the same directory `COPY`s as the real `Dockerfile`, then a `RUN` counting files):

| | `__pycache__` | `.pyc` | `.egg-info` | `elpa/` | `.git` |
|---|---|---|---|---|---|
| before | 2 | 60 | 0 | 0 | 0 |
| after | 0 | 0 | 0 | 0 | 0 |

A full `make image` was not run: only exclusions changed, the probe exercises the same directory
`COPY`s, and none of the newly excluded paths is named by a `COPY`.
