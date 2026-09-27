# Lean image for nested-podman builds — what "minimal" means for geometricalgebra

**Status:** DONE 2026-09-27 (William Emerison Six <billsix@gmail.com>) — implemented, gate-verified,
and rewritten onto the decided `MINIMAL_IMAGE` signal; ready to archive once the maintainer commits.
The maintainer's 2026-09-27 decisions settled the design: (a) the lean signal is its own name
**`MINIMAL_IMAGE`**, decoupled from `NESTED_PODMAN` (run-capability only) —
runClaudeInContainer `tasks/decouple-minimal-image-from-nested-podman.md`; (b) it is **opt-in** — the
sandbox does NOT auto-set it, so a nested `make image` builds FULL unless you pass `MINIMAL_IMAGE=1`;
(c) the nested store is moving to a disk directory + `additionalimagestores`
(runClaudeInContainer `tasks/dir-backed-nested-podman-storage.md`), which is why lean is opt-in rather
than a nested necessity. One of the per-project children of
runClaudeInContainer `tasks/minimal-image-for-nested-podman-standard.md` (the convention: every optional-feature build flag defaults to its lean value when
`NESTED_PODMAN=1`); the fleet-wide findings table is runClaudeInContainer `tasks/reference/minimal-nested-images.md`. Created 2026-09-10 at the maintainer's
request (William Emerison Six <billsix@gmail.com>: "go through all of my projects with CLAUDE.md …
research what a minimal nested podman container would be for them").
**Priority:** 3
**Difficulty:** 4

## Done (2026-09-27)

Implemented the lean-when-nested flag defaults, built the lean image nested, ran the gate.

- **Signal: `MINIMAL_IMAGE` (opt-in), not `NESTED_PODMAN`.** First implemented on the old
  `$(if $(filter 1,$(NESTED_PODMAN)),0,1)` idiom, then rewritten per the maintainer's 2026-09-27
  decision to a dedicated `MINIMAL_IMAGE` signal (the 2026-09-12 decoupling found `NESTED_PODMAN`
  conflates run-capability with build-content; this extends the fix — `NESTED_PODMAN` now drives
  only `PODMAN_RUN_FLAGS` here). Verified: plain `make image` → full (all features 1);
  `make image MINIMAL_IMAGE=1` → lean (all features 0).
- **Flags added (`?= $(if $(filter 1,$(MINIMAL_IMAGE)),0,1)` in the Makefile; ARG default 0 in the
  Dockerfile):** `USE_EMACS` (made live — was a dead ARG), `BUILD_DOCS` (was plain `?= 1`), new
  `USE_JUPYTER`, new `USE_LEAN`. `USE_SPYDER` stays 0 everywhere.
- **Emacs** moved out of `01-install-base.sh` into a new `entrypoint/05-install-emacs.sh`, dispatched
  by `USE_EMACS` (this is what makes the ARG live).
- **`03-install-notebook-tex.sh`** (pandoc + XeLaTeX for nbconvert PDF export) now runs when
  `USE_JUPYTER=1` **OR** `BUILD_DOCS=1` — the Sphinx-book block `04-install-docs.sh` depends on the
  "recommended" TeX collections `03` installs, so the docs build still gets them.
- **`install-lean.sh`** (Lean 4 theorem-prover toolchain, curl-installed) now runs only when
  `USE_LEAN=1`; the `PATH` entry stays unconditional (harmless when the dir is absent).
- **Results.** Lean nested image (all four flags 0): **2.42 GB**, `make test` = **649 passed**.
  Full image (host defaults, all flags 1): **7.21 GB** — the lean image is **~67% smaller** (saves
  ~4.8 GB, mostly TeX + the Lean toolchain). Both built cleanly nested in the 32 GB store. Host
  `make image` (no `NESTED_PODMAN` in the env) stays effectively byte-identical to before
  (emacs/notebook-tex/lean/docs all still installed).
- **CLAUDE.md documented.** Added a `make image MINIMAL_IMAGE=1` bullet to the "Dev workflow" section:
  what the lean image is for (gate/CI/nested), the sizes, exactly what it drops and how to add any one
  feature back, and that `MINIMAL_IMAGE` is separate from `NESTED_PODMAN`.

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
