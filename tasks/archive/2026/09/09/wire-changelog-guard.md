# Wire `tools/check_changelog.py` into the gate (version ↔ changelog consistency)

**Status:** **DONE 2026-09-09** — wired into both places the task proposed: `entrypoint/format.sh` (the real gate) and a host-side `make check-changelog` target, plus the gate line in `CLAUDE.md`. Verified passing on the current tree (0.0.20) and failing with a clear message on a changelog copy with that heading removed; `make format` green in-container. Rationale lives in `tasks/reference/design-decisions.md`.
**Priority:** 4
**Difficulty:** 1

## BLUF

`tools/check_changelog.py` exits 1 when `pyproject.toml`'s `version` has no `## [<version>]` heading in
`CHANGELOG.md`. It would have stopped 0.0.19 from shipping unlogged (2026-09-05: `[Unreleased]` was
empty and the release went out without an entry — the entry was written retroactively on 2026-09-06).
Wire it into the gate so a version bump without its changelog promotion turns `make format` red.

## Verified

- Passes on the current tree (0.0.19 has its heading).
- Fails with a clear message on a copy of the changelog with that heading removed
  (`--changelog <tmp>`), and on a pyproject without a `version =` line.

## Proposed wiring (choose; recommend both)

1. **`entrypoint/format.sh`** — one more accumulated step, after the `ty check` lines and in the same
   shape (every step runs; any failure fails the script):
   ```sh
   python tools/check_changelog.py || status=1
   ```
   This is the real gate (it runs in-container via `make format`, and `make format` is what the
   maintainer runs before a release).
2. **`Makefile`** — a documented target beside `check-regions`, for running it alone on the host:
   ```make
   .PHONY: check-changelog
   check-changelog: ## Verify CHANGELOG.md has a heading for pyproject.toml's version
   	python tools/check_changelog.py
   ```
   No container needed (pure Python, reads two files), so no `PODMAN_RUN_FLAGS`.

Then one line in this repo's `CLAUDE.md` gate description; the release checklist in the shared
conventions already says promotion is part of the bump.

## Why not more

It deliberately does not check that `[Unreleased]` is non-empty (a release with nothing consumer-facing
is legitimate) and cannot know whether an unlogged *change* exists — that is the reconciliation rule
(`<last tag>..HEAD` vs `[Unreleased]` at squash, session end and release) in the shared conventions.
