# GitHub Actions: check CI (phase 1), then releases (phase 2)

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Started:** 2026-09-17 (William Emerison Six <billsix@gmail.com>)
**Needs:** the maintainer's answers to the Open questions below (runner environment; container
registry).

Replicated from the modelviewprojection CI task
(`github.com/billsix/modelviewprojection`, `tasks/github-actions-format-ci.md`), adapted to
geometricalgebra's nature as a **PyPI-published library** (mvp is a private book/app). The
governing principle below is the same and is the point of the task.

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

- [ ] **Phase 1 (this task):** add a **`make check-format`** target (= `make format` +
      `git diff --exit-code`) and a check workflow that is just `checkout` → `make check-format`
      (and, per the maintainer's call, optionally `make test` / `make check-regions` /
      `make check-generated` / `make check-changelog` as further `checkout` → `make <target>`
      jobs). All fail-logic lives in the make targets, so each is one command locally.
- [ ] **Document the principle (end of Phase 1):** capture "CI is a thin wrapper over the
      make/Dockerfile system; every workflow is `checkout` → `make <target>`; all logic lives in
      make targets that run locally" as a durable convention — a concise rule in `CLAUDE.md`, or a
      `tasks/reference/` doc if it needs the fuller rationale/examples. (This is the same
      documentation step the mvp task carries; the principle should not stay buried in a task doc.)
- [ ] **Line item → spawn a NEW task (Phase 2)** once Phase 1 lands: on **tagged releases**,
      publish to **PyPI** (the existing `release`/`upload` path, or its non-interactive CI
      equivalent using a token secret) **and** optionally push a container image to a registry
      (ghcr.io) **and** attach release artifacts (the `dist` sdist/wheel + the `docs` HTML/PDF
      book) — each as the `make` target the workflow calls (`make dist`, `make docs`,
      `make image-export`/push), not inline YAML. Reconcile with the version-tag guard already in
      `make release`.

## Open questions

1. **Check workflow's runner environment** — the checks need the container image (the make targets
   build/run it). Which runner environment should the Action use (build the image in-workflow from
   the committed Dockerfile — simplest, fully self-contained — vs pull a prebuilt one)?
2. **Scope of the phase-1 check job** — format-check only, or also `test` / `check-regions` /
   `check-generated` / `check-changelog` on every PR? (`test-all-dims` is too slow for per-PR;
   nightly/manual if wanted.)
3. **Container registry** — ghcr.io for the image artifact in phase 2? (PyPI is the package
   registry either way.)

## See also

- `github.com/billsix/modelviewprojection` › `tasks/github-actions-format-ci.md` — the origin of
  this idea and the shared governing principle.
