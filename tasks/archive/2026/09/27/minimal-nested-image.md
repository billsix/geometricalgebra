# Lean image for nested-podman builds — what "minimal" means for geometricalgebra

**Created:** 2026-09-10 · **Completed:** 2026-09-27 (William Emerison Six <billsix@gmail.com>)
**Part of:** github.com/billsix/runClaudeInContainer `tasks/minimal-image-for-nested-podman-standard.md`
(one of its per-project children; the fleet-wide findings table is github.com/billsix/runClaudeInContainer
`tasks/reference/minimal-nested-images.md`)

**Superseded:** the task was first designed and implemented with image content keyed off
`NESTED_PODMAN`; image content now keys off a separate `MINIMAL_IMAGE` opt-in, not `NESTED_PODMAN`
(see github.com/billsix/runClaudeInContainer
`tasks/archive/2026/09/27/decouple-minimal-image-from-nested-podman.md`). The final implementation
recorded below already uses `MINIMAL_IMAGE`.

## Goal

The maintainer asked (2026-09-10): "go through all of my projects with CLAUDE.md … research what a
minimal nested podman container would be for them". For gacalc: a lean image that fits a nested
store and still runs the `make test` gate, while a host `make image` stays effectively unchanged.
The standard's rules (decided by the maintainer 2026-09-10): dnf-only, and a project's gates and
product build deps are never trimmed — only editors, docs toolchains, notebooks, GUI extras. The
pattern followed `PODMAN_RUN_FLAGS` applied to build flags (reference implementation:
runCrushInContainer `client/Makefile`, `FULL_TOOLCHAIN`).

## Findings (2026-09-10)

Flags were `USE_SPYDER` (0), `USE_EMACS` (0), `BUILD_DOCS` (1), but `entrypoint/01-install-base.sh`
installed `emacs` + `emacs-gtk+x11` unconditionally and `03-install-notebook-tex.sh` (pandoc,
texlive-xetex, two collections, adjustbox, …) ran unconditionally — so `USE_EMACS` was a dead ARG and
even a lean image carried a TeX distribution. The venv, pyright and the editable install are the
test environment and stay. Flag-coverage note: a change to anything the docs build consumes
(docstrings with doc-regions, `book/`) needs `BUILD_DOCS=1`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-27)

1. **The lean signal is its own name, `MINIMAL_IMAGE`**, decoupled from `NESTED_PODMAN`, which is
   run capability only and now drives only `PODMAN_RUN_FLAGS` here. The 2026-09-12 decoupling had
   found `NESTED_PODMAN` conflating run capability with build content; this extended that fix.
2. **Opt-in:** the sandbox does not auto-set it, so a nested `make image` builds the full image unless
   `MINIMAL_IMAGE=1` is passed.
3. **Why opt-in rather than a nested necessity:** the nested store moved to a disk directory +
   `additionalimagestores` (github.com/billsix/runClaudeInContainer
   `tasks/archive/2026/09/27/dir-backed-nested-podman-storage.md`).

## What changed

- **Flags** `USE_EMACS` (made live), `BUILD_DOCS` (was plain `?= 1`), new `USE_JUPYTER`, new
  `USE_LEAN`, each `?= $(if $(filter 1,$(MINIMAL_IMAGE)),0,1)` in the Makefile with ARG default 0 in
  the Dockerfile; `USE_SPYDER` stays 0 everywhere. The first implementation used
  `$(if $(filter 1,$(NESTED_PODMAN)),0,1)` and was rewritten onto `MINIMAL_IMAGE` per decision 1.
- **Emacs** moved out of `01-install-base.sh` into a new `entrypoint/05-install-emacs.sh`, dispatched
  by `USE_EMACS`.
- **`03-install-notebook-tex.sh`** (nbconvert PDF export) runs when `USE_JUPYTER=1` **or**
  `BUILD_DOCS=1`, because the Sphinx-book `04-install-docs.sh` depends on the TeX collections `03`
  installs.
- **`install-lean.sh`** (Lean 4, curl-installed) runs only when `USE_LEAN=1`; its `PATH` entry stays
  unconditional (harmless when absent).
- **`CLAUDE.md`** gained a `make image MINIMAL_IMAGE=1` bullet in "Dev workflow": what the lean image
  is for (gate / CI / nested), the sizes, what it drops and how to add one feature back, and that
  `MINIMAL_IMAGE` is separate from `NESTED_PODMAN`.

## Verification

Plain `make image` → full (all features 1); `make image MINIMAL_IMAGE=1` → lean (all features 0). The
lean image is **2.42 GB** and passes `make test` (649 passed); the full image is **7.21 GB**, so lean
is ~67% smaller (~4.8 GB saved, mostly TeX and the Lean toolchain). Both built cleanly nested in the
32 GB store, and the host `make image` remained effectively byte-identical to before.
