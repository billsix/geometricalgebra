# GitHub Actions: check CI (phase 1), then releases (phase 2)

**Created:** 2026-09-17 · **Completed:** 2026-09-26 (William Emerison Six <billsix@gmail.com>)

The maintainer asked for "a github action that will pass if the code is formatted correctly … via
running make format, to see if there is a git diff … then, on tagged releases, push to a registry and
make a release tarball … then do this on other projects such as geometricalgebra". This task was
that "other project", replicating the github.com/billsix/modelviewprojection CI work (its task doc
no longer exists) and adapted to gacalc being a PyPI-published library rather than a book/app. There
was no `.github/` before. The durable CI rules now live in `CLAUDE.md` › "Continuous integration".

## Governing principle — CI is a thin wrapper over the make/Dockerfile system

Every workflow is `checkout` → `make <target>`; all real work lives in the Makefile + Dockerfile so it
runs identically on a laptop and in CI. A step CI needs becomes a `make` target first.
`CONTAINER_CMD` auto-detects podman → docker, so the same target runs on a GitHub runner and on the
host. Local runnability is the acceptance test; anything that only works in GitHub's environment is a
smell.

## Decisions

1. **Runner:** `ubuntu-latest`, with the image built in-workflow from the committed Dockerfile, lean
   flags (`BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0`).
2. **`check-generated` / `check-regions` in CI: yes** (2026-09-26), both containerized;
   `check-changelog` already runs inside the `format` job (it is in `format.sh`); `test-all-dims`
   (g1–g5, ~1.5 h) stayed manual, too slow per PR.
3. **Phase 2 (PyPI publish on tag) was spun off** (2026-09-26) to
   `tasks/archive/2026/10/22/github-actions-pypi-publish-on-tag.md`, since it needed a maintainer
   decision and one-time PyPI Trusted-Publishing configuration.
4. **Carried over from mvp:** `actions/checkout@v5` (Node 24) from the start, since mvp hit the Node
   20 deprecation with `@v4`; a `make check-format` target (`make format` + `git diff --exit-code`).
   gacalc's `make format` regenerates the gitignored `g*.py` (so they don't trip the diff), runs ruff
   at 88 columns (mvp uses 80), `ty`, and `check_changelog`.
5. **Not carried over:** mvp's bake-source change was mostly moot — gacalc's Dockerfile already
   `COPY`s `src`/`tools`/`pyproject` into `/gacalc` and installs at build, and gacalc pushes no
   container image (it publishes to PyPI). gacalc's own `tools/check_annotations.py` (an
   exemptions-catalogue check, not mvp's `check_local_annotations.py`) was not wired into CI; `ty`
   covers type-checking.

## What changed

- **Phase 1 (2026-09-18):** `make check-format` and `.github/workflows/checks.yml` with check-only
  jobs `format` and `test` on push + PR; neither commits or reformats. A "## Continuous integration"
  section was added to `CLAUDE.md`.
- **CI fix (2026-09-26):** the first real run failed the `test` job with `Error 125` — `run … gacalc`
  tried to pull `gacalc:latest` — because `make test` had no `image` prerequisite, unlike `format`,
  `docs` and `jupyter`. It was invisible locally because a host image already existed. Fixed with
  `test: image`, plus `shell-exec: image` (matching the conformance spec) and `dist: image` (matching
  its own "Needs the image built" comment); `make -n test` then emitted `podman build -t gacalc`
  before the `run`.
- **`generated` job (2026-09-26):** `check-generated` and `check-regions` had run
  `python tools/gen_specialized.py` on the host, needing sympy, which a bare runner lacks. Both became
  `: image` targets running inside the image via a minimal `podman run` (like `test`), not
  `shell-exec`, whose `SHELL_RUN_FLAGS` carry X11/Wayland/port passthrough unsuitable for a headless
  runner. A third job `generated` runs both (the second's `image` prereq hits the layer cache).

## Verification

2026-09-18: `make check-format BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` exit 0 (regenerate + ruff + ty
+ changelog + clean diff); `make test` with the same flags 490 passed (reusing a pre-built host image,
which is why the missing prereq slipped through). 2026-09-26: `check-generated` and `check-regions`
green locally in their containerized form.
