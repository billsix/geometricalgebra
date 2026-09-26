# GitHub Actions: check CI (phase 1), then releases (phase 2)

**Status:** Phase 1 COMPLETE. 2026-09-18 initial (`make check-format` + `.github/workflows/checks.yml`).
**2026-09-26:** (a) CI fix — the `test` job failed on a fresh runner (`Error 125`, tried to pull
`gacalc:latest`) because `make test` lacked an `image` prereq; fixed (`test: image`, plus
`shell-exec: image` / `dist: image` for consistency). (b) Q2 done — containerized `check-generated`
and `check-regions` (they need sympy, absent on a bare runner) and added a third CI job `generated`
running both. Now four check jobs: `format`, `test`, `generated` (×2 steps). (c) Phase 2 (PyPI
publish on tag, old Q3) spun off to `tasks/github-actions-pypi-publish-on-tag.md`. Staged for the
maintainer to commit.
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
- **`check-generated` and `check-regions` — added to CI 2026-09-26 (Q2 resolved).** They ran bare
  `python tools/gen_specialized.py` on the **host** (sympy, which a bare ubuntu runner lacks), so they
  were first **containerized** — both now `: image` and run the regen+check inside the image via
  `podman run` (mirroring `test`'s minimal invocation, NOT `shell-exec`, whose `SHELL_RUN_FLAGS`
  carry X11/Wayland/port passthrough unsuitable for a headless runner). A third `checks.yml` job
  `generated` runs `make check-generated` then `make check-regions` (one job, two steps: the second's
  `image` prereq hits the build-layer cache). Both verified green locally 2026-09-26.
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
- [x] **CI fix + Q2 (DONE 2026-09-26):** `test: image` (the missing prereq that broke the first real
      CI run), plus `shell-exec: image` / `dist: image` for consistency; containerized
      `check-generated` / `check-regions` and added the `generated` CI job. See Status.
- [→] **Phase 2 — PyPI publish on tag: SPUN OFF** to `tasks/github-actions-pypi-publish-on-tag.md`
      (needs a maintainer decision + one-time PyPI Trusted-Publishing config). See that task.

## Open questions

1. ~~Runner environment~~ **RESOLVED:** `ubuntu-latest`, image built in-workflow from the committed
   Dockerfile (self-contained), lean flags. `CONTAINER_CMD` auto-detects podman→docker.
2. ~~Add `check-generated` / `check-regions` to CI?~~ **RESOLVED 2026-09-26:** yes — both
   containerized (`: image`, run via the image) and added as the `generated` CI job. `check-changelog`
   already runs inside the `format` job (it's in `format.sh`); `test-all-dims` stays manual/nightly
   (too slow per-PR).
3. ~~Phase 2 PyPI automation~~ **SPUN OFF 2026-09-26** to
   `tasks/github-actions-pypi-publish-on-tag.md` — the Trusted-Publishing-vs-manual decision lives
   there now.

## Phase-1 CI fix (2026-09-26, William Emerison Six <billsix@gmail.com>)

The first real CI run failed the `test` job with `Error 125`: `docker/podman run ... gacalc` tried
to **pull** `gacalc:latest` from a registry (access denied / 404). Root cause: `make test` had **no
`image` prerequisite**, unlike every other containerized target (`format: image`, `docs: image`,
`jupyter: image`). On the maintainer's host `make test` worked because an image already existed from
a prior `make image`/`make all`; on a fresh runner nothing built it. **Why "verified locally" below
didn't catch it:** the local 490-passed run reused a pre-built host image, so the missing prereq was
invisible until a clean-checkout runner.

Fix (`Makefile`): `test: image`, and — same latent drift, not the cause of this failure —
`shell-exec: image` (matches the conformance spec) and `dist: image` (matches its own "Needs the
image built" comment). Verified `make -n test` now emits `podman build -t gacalc` before the `run`.

## Verified locally (2026-09-18)
- `make check-format BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` → exit 0 (regenerate + ruff + ty +
  changelog + clean `git diff`).
- `make test BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` → **490 passed** (note: reused a pre-built host
  image — see the Phase-1 CI fix above).

## See also

- `github.com/billsix/modelviewprojection` › `tasks/github-actions-format-ci.md` — the origin of
  this idea and the shared governing principle.
