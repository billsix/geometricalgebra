# Lean image for nested-podman builds — what "minimal" means for geometricalgebra

**Status:** proposed — research done 2026-09-10 (survey of the Dockerfile + Makefile from the
runClaudeInContainer sandbox); **implementation needs go-ahead**. One of the per-project children of
runClaudeInContainer `tasks/minimal-image-for-nested-podman-standard.md` (the convention: every optional-feature build flag defaults to its lean value when
`NESTED_PODMAN=1`); the fleet-wide findings table is runClaudeInContainer `tasks/reference/minimal-nested-images.md`. Created 2026-09-10 at the maintainer's
request (William Emerison Six <billsix@gmail.com>: "go through all of my projects with CLAUDE.md …
research what a minimal nested podman container would be for them").
**Priority:** 3
**Difficulty:** 4

## BLUF

Make `make image` inside a sandbox (which exports `NESTED_PODMAN=1`) build a lean image that fits
the nested RAM store and still runs this project's gate, while a host `make image` stays
byte-identical — via the idiom `FLAG ?= $(if $(filter 1,$(NESTED_PODMAN)),0,1)` on each optional-feature flag (the `PODMAN_RUN_FLAGS`
pattern applied to build flags; reference implementation: runCrushInContainer `client/Makefile`,
`FULL_TOOLCHAIN`). Done = the flags below carry the nested-aware default, a nested `make image`
builds and passes the gate, both image sizes are measured and recorded here and in `CLAUDE.md`.

## Context — read first

- runClaudeInContainer `tasks/reference/minimal-nested-images.md` — the standard, the idiom, the rules (a project's *gates* and *product build deps* are never
  trimmed; only editors, docs toolchains, notebooks, GUI extras), and every project's row.
- This repo's `Dockerfile`, `Makefile` (flag block + `image` target), `entrypoint/*install*.sh`.
- The flag-coverage rule (cross-project `CLAUDE.md` › "Verification gates in nested containers"): a
  lean build verifies nothing about the layers it skips — when a change touches what a skipped layer
  consumes, build with that flag ON.

## Findings (2026-09-10)

**What the image installs today.** Flags `USE_SPYDER` (0), `USE_EMACS` (0), `BUILD_DOCS` (1). **But** `entrypoint/01-install-base.sh` installs `emacs` + `emacs-gtk+x11` unconditionally, and `03-install-notebook-tex.sh` (pandoc, texlive-xetex, two collections, adjustbox…) runs unconditionally — so `USE_EMACS` is a dead ARG (declared in the Dockerfile, never tested) and the lean image still carries a TeX distribution. The venv + pyright + the editable install are the product's test environment and stay.

**What "minimal" is here.** `BUILD_DOCS` → lean when nested; `emacs*` moved out of `01-install-base.sh` behind the (currently dead) `USE_EMACS`; `03-install-notebook-tex.sh` behind `USE_JUPYTER` (new) or folded under `BUILD_DOCS` — it exists for nbconvert's PDF export, a notebook feature, not a test dependency.

**Notes.** A change to anything the docs build consumes (docstrings with doc-regions, `book/`) needs `BUILD_DOCS=1` nested — the flag-coverage rule from spimulator 2026-07-07 applies.

## Plan

- [ ] `01-install-base.sh`: drop `emacs`, `emacs-gtk+x11`; new `02-install-emacs.sh` (or reuse the Spyder pattern) run under `USE_EMACS=1` — this makes the existing ARG live.
- [ ] Dockerfile: run `03-install-notebook-tex.sh` under a flag (`USE_JUPYTER`, Makefile default 1 on host); document which feature it serves.
- [ ] Makefile: `BUILD_DOCS`, `USE_EMACS`, `USE_JUPYTER` get the nested-aware default (`USE_SPYDER` stays 0 everywhere).
- [ ] Gate check: `make test` (the CLAUDE.md gate) must pass in the lean image; `make html` is a docs-only path and is what `BUILD_DOCS=1` is for.
- [ ] Measure both images; record in `CLAUDE.md`.
- [ ] Record both sizes (host full vs nested lean) here and in `CLAUDE.md`; add the standard's one-line
      rule to `CLAUDE.md` ("nested = lean image automatically; `FLAG=1` overrides").

## Open questions

None — the standard's decisions (dnf-only, gates never trimmed) were the maintainer's on 2026-09-10;
anything project-specific to decide is flagged inline above.
