# Host-run Makefile targets call `python3`, not `python`

**Status:** in progress
**Priority:** 2
**Difficulty:** 1
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

On one of the maintainer's machines `make shell` fails with "python: not found": the host has
`python3` but no `python`. Change the Makefile recipes that run **on the host** (`generate`,
`generate-all`, `check-changelog`, and whatever `make shell`'s prerequisites invoke) to `python3`.
Recipes inside `podman run … -c '… source /venv/bin/activate …'` run the venv's `python`, which
always exists, and can stay. Done means: `rg -n '\bpython\b' Makefile` shows only in-container
uses, `make shell` works on a host without `python`, and `make help` is unchanged.
