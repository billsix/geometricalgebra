# GitHub Actions: check CI (phase 1), then releases (phase 2)

**Status:** Phase 1 IMPLEMENTED 2026-09-18 (`make check-format` + `.github/workflows/checks.yml`,
two jobs: `format` + `test`). Phase 2 (PyPI publish on tag) is proposed — needs the maintainer's
PyPI-CI decision (see below). Staged for the maintainer to commit.
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-09-17 (William Emerison Six <billsix@gmail.com>)

Replicated from the modelviewprojection CI work
(`github.com/billsix/modelviewprojection`, `tasks/github-actions-format-ci.md`), applying what that
session learned, adapted to geometricalgebra's nature as a **PyPI-published library** (mvp is a
private book/app). The governing principle below is the same.

## Applied from the mvp session (2026-09-18)

- **`checkout@v5`** (Node 24) from the start — mvp hit the Node 20 deprecation warning with `@v4`.
- **Added a `make check-format` target** (`= make format` + `git diff --exit-code`), mirroring mvp,
  so the format gate is one command. gacalc's `make format` regenerates the gitignored `g*.py`, runs
  ruff (`--line-length=88`, not mvp's 80) + `ty` + `check_changelog`; the generated modules are
  gitignored so they don't trip the diff.
- **`checks.yml` = two check-only jobs**, `format` (`make check-format`) and `test` (`make test`),
  on push + PR, `checkout` → `make <target>`, lean flags (`BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0`).
  Both are container-run thin wrappers; neither commits/reformats the repo.
- **`check-generated` and `check-regions` were NOT added to CI** (unlike the format/test pair): both
  run `python tools/gen_specialized.py` on the **host** (they need sympy on the runner, which a bare
  ubuntu runner lacks). To CI them, they'd have to be containerized first (run via the image). Left
  as a deferred enhancement — flag Q2.
- **Bake-source (mvp's headline change) is largely already done here:** gacalc's Dockerfile already
  `COPY`s `src`/`tools`/`pyproject` into `/gacalc` and installs at build, so a gacalc image already
  carries its source. gacalc also does **not push a container image** (no `image-push`; it publishes
  to **PyPI**), so "a pulled image runs standalone" is not a current gacalc goal — the bake-source
  refinement mostly does not apply.
- **gacalc has its own annotation checker** (`tools/check_annotations.py`, an exemptions-catalogue
  check — different from mvp's `check_local_annotations.py`). Not wired into CI here; `make format`'s
  `ty` covers type-checking. Could be added later if wanted.

## Goal

There is no CI today (`.github/` does not exist). Add GitHub Actions, in phases: first a
check-only workflow that fails on unformatted / broken code, then release automation on tagged
releases. This mirrors the maintainer's mvp request ("a github action that will pass if the code
is formatted correctly … via running make format, to see if there is a git diff … then, on tagged
releases, push to a registry and make a release tarball … then do this on other projects such as
geometricalgebra") — this task is that "other project".

This is a **phased** task — the structure below is deliberate.

## Governing design principle — CI is a THIN WRAPPER over the make/Dockerfile system

**Every workflow does as little as possible: `checkout` → `make <target>`. All real work lives in
the Makefile + Dockerfile so it runs identically on a laptop and in CI** — no build/test/release
logic in YAML. What CI does must be reproducible locally with the same command, not a GitHub-only
path that drifts from what the maintainer runs by hand.

geometricalgebra is already built for this — nearly every CI step is an existing make target:

- **If a workflow needs a step, it must be a `make` target first**, then the workflow calls it. The
  format-check is a single target (e.g. `make check-format` = `make format` + `git diff
  --exit-code`) so the exact CI behaviour is one command locally. Same for every other check and
  for the release steps.
- **`CONTAINER_CMD` already auto-detects podman→docker** (`Makefile:11`), so the identical `make`
  target runs on a GitHub runner (Docker) and on the maintainer's host (podman). No
  podman-vs-docker branching in the workflow.
- **Local runnability is the acceptance test**, not just "the Action is green": because the
  workflow only calls a `make` target, the maintainer reproduces exactly what CI does by running
  that same target (nested podman drives the container). No GitHub-runner simulator needed. A thing
  that can only be done in GitHub's environment is a smell to flag, not design around.
- This mirrors the shared container-template convention (make drives the container; scripts run
  both in-container and on the host from the repo root).

## Context

- **No CI today** — no `.github/`. The standing gates are the make targets, all container-driven
  and host-reproducible.
- **The check targets already exist** and are the phase-1 building blocks: `format` (regenerate +
  ruff + ty), `test`, `check-regions` (doc-region markers), `check-changelog` (CHANGELOG has a
  heading for pyproject's version), `check-generated` (codegen is deterministic — regen twice,
  compare). `test-all-dims` is the SLOW full-dim gate (generates g1..g5, ~1.5h) — a nightly/manual
  candidate, not the per-PR check.
- **The release targets already exist** for phase 2: `dist` (sdist + wheel), `upload` / `upload-test`
  (twine to PyPI / TestPyPI), `release` (host version-tag guard + upload + git tag), `docs`
  (Sphinx book → HTML + PDF into `output/gacalc/`), and `image-export` / `image-import`.
- geometricalgebra publishes to **PyPI**, so its release story is PyPI-first (the package), with a
  container image to a registry as a secondary artifact — unlike mvp, whose deliverable is the book.
- **Personal convention:** the agent stages, the maintainer commits — any `.github/workflows/*.yml`
  is created and staged, not committed, by the agent.

## Plan (phased)

- [x] **Phase 1 (DONE 2026-09-18):** added `make check-format` and `.github/workflows/checks.yml`
      (jobs `format` + `test`, `checkout@v5`, lean flags). All fail-logic in the make targets;
      verified locally (the same commands CI runs).
- [x] **Document the principle:** added a "## Continuous integration" section to `CLAUDE.md`
      (CI is a thin wrapper over the make/Dockerfile system).
- [ ] **Phase 2 — PyPI publish on tag (needs the maintainer's decision + one-time setup).** On a
      `v*` tag, build + publish to **PyPI**. gacalc already has a working **manual** path
      (`make dist` → `make upload` → `make release`, interactive twine + host `git tag`), so
      automating it is a real choice, not a gap. Recommended CI approach: **PyPI Trusted Publishing
      (OIDC)** — no token secret in the repo; you configure a "trusted publisher" on PyPI once
      (project → Publishing → add the repo + `release.yml`), then a `release.yml` on the `v*` tag
      runs `make dist` and publishes via `pypa/gh-action-pypi-publish`. Attach the `dist` sdist/wheel
      (and optionally the `docs` HTML/PDF) to a GitHub Release. **Not implemented here** because it
      needs your PyPI-side config and I can't test a real publish; deciding "keep manual `make
      release`" is also legitimate. (gacalc does not push a container image, so no ghcr step —
      unlike mvp.) Reuse the version-tag guard already in `make release`.

## Open questions

1. ~~Runner environment~~ **RESOLVED:** `ubuntu-latest`, image built in-workflow from the committed
   Dockerfile (self-contained), lean flags. `CONTAINER_CMD` auto-detects podman→docker.
2. **Add `check-generated` / `check-regions` to CI?** Not included yet — both run
   `python tools/gen_specialized.py` on the **host**, which a bare ubuntu runner can't (no sympy).
   To CI them they must be containerized (run via `make shell-exec`/the image). Worth doing for the
   determinism guard (`check-generated`) especially. `check-changelog` already runs inside the
   `format` job (it's in `format.sh`). `test-all-dims` stays manual/nightly (too slow per-PR).
3. **Phase 2 PyPI automation** — go with Trusted Publishing (OIDC, no secret; needs one-time PyPI
   config) on a `v*` tag, or keep the manual `make release`? (No ghcr step — gacalc doesn't push an
   image.) See the Plan.

## Verified locally (2026-09-18)
- `make check-format BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` → exit 0 (regenerate + ruff + ty +
  changelog + clean `git diff`).
- `make test BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` → **490 passed**.

## See also

- `github.com/billsix/modelviewprojection` › `tasks/github-actions-format-ci.md` — the origin of
  this idea and the shared governing principle.
