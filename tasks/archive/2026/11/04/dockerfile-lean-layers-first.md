# Lean layers first in the Dockerfile, and an offline pyright — done-record

**Completed:** 2026-11-04. Requested by William Emerison Six <billsix@gmail.com>: "investigate whether
putting lean earlier in the dockerfile will help. right now, the download time and build time for the
lean stuff takes a long time. to make it so changes don't require a full rebuild of that, knowing that
dockerfiles have cached layers, perhaps it should be put earliest in the dockerfile as reasonable." The
same change carried the offline-pyright fix from
`tasks/archive/2026/11/04/emacs-python-lsp-investigation.md` ("Follow-ups"). Implemented by the agent
after the maintainer's "go".

## What was found

- **A build-arg's value is part of the cache key of every later `RUN`, used or not.** Measured with
  podman: a throwaway `ARG UNUSED` + `RUN` Containerfile was cached at the same value and rebuilt at a
  new one. Docker documents the same. With all seven `ARG`s at the top, bumping `EPIX_COMMIT` (as the
  ePiX pin bump earlier on 2026-11-04 did) or toggling any `USE_*` flag re-downloaded Lean and Mathlib.
- Everything above the Lean layers busted them too: any dotfile edit (`COPY entrypoint/dotfiles/`), any
  `0N-install-*.sh` edit, and the base `RUN`, including the pyright install the offline fix had to edit.
- `install-lean.sh` installed elan's floating `stable` toolchain, and `lake` then fetched the
  `proofs/lean-toolchain` pin (`v4.34.1`) as a second toolchain whenever the two differed.
- The pip `pyright` package is a launcher that downloads Node and the server on first use in each fresh
  container, so Emacs had no pyright offline (details in the investigation record above).

## What changed

- **`Dockerfile` order:** `FROM` → `dnf upgrade` → `ARG USE_LEAN` → Lean toolchain → Mathlib bake →
  then each remaining `ARG` declared just before the first layer that reads it (`USE_SPYDER`/`USE_EMACS`
  before the base layer, `USE_JUPYTER`/`BUILD_DOCS` before the TeX layers, `USE_EPIX`/`EPIX_COMMIT`
  before ePiX). The header comment explains the rule; the Lean block's CACHE ORDERING comment says why
  it is first.
- **`entrypoint/install-lean.sh`** installs only the toolchain pinned in `proofs/lean-toolchain`
  (elan-init's `--default-toolchain`; `$LEAN_TOOLCHAIN` from the Dockerfile, or the repo file when run on
  a host). Its `set -e` became `set -eo pipefail`, so a failed `curl` in the `curl | sh` pipe now fails
  the build.
- **Pyright** is installed by `entrypoint/01-install-base.sh` as `dnf install nodejs npm` + `npm install
  -g pyright` (always on, since `make check-notebooks` uses it as well as Emacs). The Dockerfile's
  `uv pip install pyright` and the pyright-only `libatomic` install were removed.
- Docs: `tasks/reference/emacs-lsp-setup.md` (how pyright is installed and why not pip, the ty fallback,
  how lsp-mode shows parameter hints, and the 2026-11-04 headless verification); the stale `.dockerignore`
  comment (it described a build-time MELPA install that no longer exists); the `Makefile`
  `check-notebooks` comment now names where pyright is installed. No `CHANGELOG.md` entry: the image is
  not part of the published library.

## Verification (2026-11-04)

- `make image`: exit 0. The build log shows one Lean toolchain installed, `leanprover/lean4:v4.34.1`.
- **Cache:** a rebuild with different `USE_SPYDER` and `USE_EPIX` values took the dnf-upgrade, Lean,
  Mathlib and dotfiles layers from cache and started rebuilding only at the base layer that reads
  `USE_SPYDER` (stopped there; the test only needed the cache hits). The later `make lean`/`make test`
  rebuild was all cache hits (27 of 27 steps).
- **Offline pyright:** headless Emacs with the real `init.el`, under `--network=none`: pyright
  (`/usr/local/bin/pyright-langserver`) and ruff attached; completion after `g3.e_1.` and signature help
  inside `g3.e_1.project(` both answered. `pyright notebooks/` offline: pyright 1.1.414, 0 errors.
- `make lean`: OK (proofs build, no `sorry`/`admit`). `make test`: 717 passed.
- `make format` was not run: no Python changed.

## Left to the maintainer

A host rebuild and an Emacs try-out, and then recording the convention (npm pyright, never the pip
launcher; declare each `ARG` where it is first used) wherever it fits — this repo's `CLAUDE.md`, the
github.com/billsix/runClaudeInContainer / github.com/billsix/runCrushInContainer shared conventions,
or the maintainer's personal overlay.
