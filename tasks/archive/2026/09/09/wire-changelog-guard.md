# Wire `tools/check_changelog.py` into the gate (version ↔ changelog consistency)

**Created:** 2026-09-06 · **Completed:** 2026-09-09

## Why

`tools/check_changelog.py` exits 1 when `pyproject.toml`'s `version` has no `## [<version>]` heading
in `CHANGELOG.md`. It would have stopped 0.0.19 from shipping unlogged: on 2026-09-05 `[Unreleased]`
was empty and the release went out without an entry, written retroactively on 2026-09-06. Wiring it
into the gate makes a version bump without its changelog promotion turn `make format` red. Rationale
lives in `tasks/reference/design-decisions.md`.

## What changed

Both proposed wirings were done:

1. **`entrypoint/format.sh`** — `python tools/check_changelog.py || status=1`, after the `ty check`
   lines, in the same accumulate-every-step shape. This is the real gate (in-container via
   `make format`, which the maintainer runs before a release).
2. **`Makefile`** — a `## `-documented `.PHONY: check-changelog` target beside `check-regions`, for
   running it alone on the host; pure Python reading two files, so no container and no
   `PODMAN_RUN_FLAGS`.

Plus one line in `CLAUDE.md`'s gate description.

## Deliberately not checked

It does not require `[Unreleased]` to be non-empty (a release with nothing consumer-facing is
legitimate), and it cannot know whether an unlogged change exists — that is the reconciliation rule
(`<last tag>..HEAD` vs `[Unreleased]` at squash, session end and release) in the shared conventions.

## Verification

Passed on the tree (0.0.19 when first checked, 0.0.20 when wired); failed with a clear message on a
changelog copy with the version heading removed (`--changelog <tmp>`) and on a pyproject without a
`version =` line; `make format` green in-container.
