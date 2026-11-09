# CI: build the lean image, and run the notebook type gate

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.2

## What was wrong

`checks.yml`'s three per-push jobs passed `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0`. Since `USE_LEAN`,
`USE_EPIX` and `USE_JUPYTER` default to 1 unless `MINIMAL_IMAGE=1`, every job built Lean + Mathlib,
ePiX and the XeLaTeX set, which none of those gates use. `lean.yml` also built ePiX. CI never ran
`make check-notebooks`.

## What changed

- **`.github/workflows/checks.yml`:**
  - every job runs `make <target> MINIMAL_IMAGE=1`;
  - a new `notebooks` job runs `make check-notebooks MINIMAL_IMAGE=1` (pyright is in the base group);
  - the header comment says every job builds the lean image.
- **`.github/workflows/lean.yml`** runs `make lean MINIMAL_IMAGE=1 USE_LEAN=1`. Its comment says what
  that image contains.
- **Docs:**
  - the Makefile `check-format` comment now names `MINIMAL_IMAGE=1`;
  - `CLAUDE.md` › "Continuous integration" describes four jobs and the lean image;
  - `README.md` › "Contributing" says the same.

## Verification

- Both workflow files parse as YAML.
- `make -n` for `check-format`, `test-full`, `check-generated`, `check-regions` and
  `check-notebooks` with `MINIMAL_IMAGE=1` passes `USE_LEAN=0` to the build. `make -n lean
  MINIMAL_IMAGE=1 USE_LEAN=1` passes `USE_LEAN=1` and `USE_EPIX=USE_JUPYTER=USE_EMACS=0`.
- `make check-notebooks MINIMAL_IMAGE=1` (nested): exit 0, with 0 errors and 42 warnings (the
  display cells' unused expressions, downgraded on purpose in `pyrightconfig.json`).
- The workflows themselves can only run on GitHub. The first push of this branch exercises them.
