# Host-run Makefile targets call `python3`, not `python`

**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-10

On one of the maintainer's machines `make shell` failed with "python: not found": the host had
`python3` but no `python`. The cause was the parse-time `VERSION := $(shell python -c …)` near the
`dist`/`release` targets, which make evaluates on **every** invocation, `make shell` included. That
line and the three host-run recipes (`generate`, `generate-all`, `check-changelog`) now call
`python3`. Recipes inside `podman run … -c '… source /venv/bin/activate …'` still call the venv's
`python`, which always exists there.

Verified by running make with a `PATH` holding only `make` and `python3`: `VERSION` resolved to
`0.0.20` with no "not found", and `make help` was unchanged.
