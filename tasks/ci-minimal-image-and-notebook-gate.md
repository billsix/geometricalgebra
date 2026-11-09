# CI: build the lean image, and run the notebook type gate

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 2
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.2

## BLUF

Every per-push CI job builds the full image, Lean and Mathlib included, for gates that need none of
it. CI also never runs `make check-notebooks`. Done means:

- `checks.yml` builds with `MINIMAL_IMAGE=1`;
- `lean.yml` builds lean plus Lean (`MINIMAL_IMAGE=1 USE_LEAN=1`);
- a `notebooks` job runs `make check-notebooks`.

## Context

**What CI builds today.** `.github/workflows/checks.yml`'s three jobs pass `BUILD_DOCS=0 USE_EMACS=0
USE_SPYDER=0`. The Makefile defaults `USE_LEAN`, `USE_EPIX` and `USE_JUPYTER` to 1 unless
`MINIMAL_IMAGE=1`, so each job builds:

- the elan toolchain and the multi-GB Mathlib cache;
- ePiX from source;
- the XeLaTeX set.

`lean.yml` likewise builds ePiX and Jupyter's TeX that `make lean` doesn't use.

**What the lean image keeps.** `MINIMAL_IMAGE=1` keeps the base group, which `make test`, `make
format` and `make check-notebooks` need. pyright is in `entrypoint/01-install-base.sh`. `CLAUDE.md`
already names `MINIMAL_IMAGE=1` as the flag for "fast CI".

**The Makefile comment.** `check-format`'s comment suggests the old three-flag line.

## Plan

- [ ] `checks.yml`: `make <target> MINIMAL_IMAGE=1` in each job, plus a `notebooks` job running
  `make check-notebooks MINIMAL_IMAGE=1`.
- [ ] `lean.yml`: `make lean MINIMAL_IMAGE=1 USE_LEAN=1`. Fix its "leaner image" comment.
- [ ] Update the Makefile `check-format` comment, and `CLAUDE.md`/`README.md`'s CI descriptions.
- [ ] Verify with a YAML parse, a `make -n` dry run of each command, and a local
  `make check-notebooks MINIMAL_IMAGE=1`.

## Open questions

None.
