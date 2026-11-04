# Move the Lean toolchain + Mathlib bake to the top of the Dockerfile

**Status:** ready — decisions made; waiting on the maintainer's "go"
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-04 (William Emerison Six <billsix@gmail.com>): "investigate whether putting lean
earlier in the dockerfile will help. right now, the download time and build time for the lean stuff
takes a long time. to make it so changes don't require a full rebuild of that, knowing that dockerfiles
have cached layers, perhaps it should be put earliest in the dockerfile as reasonable."

## BLUF

Yes, it would help. The Lean toolchain and the multi-GB Mathlib download sit after the dnf, Emacs, TeX
and docs layers and after every `ARG`, so editing any of those, or changing any build-arg value (the
ePiX pin bump of 2026-11-04 did), re-downloads Lean and Mathlib. Done = the two Lean layers sit right
after `FROM` + `dnf upgrade`, with only `USE_LEAN` declared above them, and a rebuild after an
unrelated change (e.g. bumping `EPIX_COMMIT`) reuses them from cache.

## Context

- `Dockerfile` order today: `FROM` → all seven `ARG`s (`USE_SPYDER`, `USE_EMACS`, `BUILD_DOCS`,
  `USE_JUPYTER`, `USE_LEAN`, `USE_EPIX`, `EPIX_COMMIT`) → `dnf upgrade` → `COPY entrypoint/dotfiles/`
  → `COPY` the `0N-install-*.sh` scripts → base/Emacs/Spyder + venv + pyright `RUN` → notebook TeX →
  Sphinx docs → **Lean** (`COPY install-lean.sh` + `RUN`) → **Mathlib** (`COPY proofs/lakefile.toml
  lean-toolchain lake-manifest.json` + `lake exe cache get`) → ePiX → Python deps → `COPY src/tools`.
  The 2026-09-28 move already put Lean before `COPY src`, which stopped code edits from rebaking it;
  this task finishes the job for the layers above it.
- `entrypoint/install-lean.sh` needs only `git` (it `dnf install`s it) and `curl` (in the Fedora base
  image). It doesn't depend on any earlier layer, so nothing stops it from moving up.

## Findings (investigated 2026-11-04)

1. **Every `ARG` value invalidates every later `RUN`, used or not.** Measured with the sandbox's podman:
   a two-line `ARG UNUSED` + `RUN` Containerfile built with `UNUSED=1` twice gave the same image ID
   (cached), and with `UNUSED=2` a new one, though the `RUN` never reads it. Docker documents the same
   ("all RUN instructions following an ARG use the ARG variable implicitly"). Because all the `ARG`s
   are declared at the top, bumping `EPIX_COMMIT` or toggling any `USE_*` flag rebuilds Lean and
   Mathlib. The 2026-11-04 ePiX pin bump did exactly that.
2. **Layers above Lean change often.**
   - `COPY entrypoint/dotfiles/` changes with every `init.el` / `preferences.el` edit (most recently
     2026-10-30). The vendored `elpa/` itself is excluded by `.dockerignore`.
   - Editing any `0N-install-*.sh` script, or the base `RUN` (which also pip-installs pyright), busts
     Lean. The planned offline-pyright fix (`tasks/archive/2026/11/04/emacs-python-lsp-investigation.md`,
     "Follow-ups") edits that `RUN`, so under today's order it would also re-download Mathlib.
3. **Lean installs two toolchains.** `install-lean.sh` runs `elan default stable`, but `lake` then
   fetches the version pinned in `proofs/lean-toolchain` (`leanprover/lean4:v4.34.1`) whenever
   "stable" differs. Pinning the default to the `lean-toolchain` value would save one toolchain
   download. "stable" also floats, so a cache-busted rebuild can pick up a different toolchain than
   the last one.
4. **Side finding:** `.dockerignore`'s comment says the build runs `emacs --batch --load
   install-melpa-packages.el`. That step no longer exists (Emacs packages are bind-mounted).

## Plan

1. Move `ARG USE_LEAN=0`, the Lean `COPY` + `RUN`, the `ENV PATH`, and the Mathlib `COPY` + `RUN`
   to directly after the `dnf upgrade` layer, keeping their comments. Leave `dnf upgrade` first:
   it never changes, so it stays cached.
2. Declare each remaining `ARG` just before the first layer that reads it (`EPIX_COMMIT` beside the
   ePiX block, and so on), so a flag only invalidates its own layers and the ones after them. Keep the
   `ARG` comments with their `ARG`s.
3. Make `install-lean.sh` install the toolchain named in
   `proofs/lean-toolchain` instead of `stable`.
4. Fix the stale `.dockerignore` comment.
5. Verify: `make image`, then bump a later input (e.g. a throwaway `EPIX_COMMIT` build-arg or a touched
   `init.el`) and confirm the build log shows the Lean and Mathlib steps as cache hits. Also, `make lean`
   and `make test` still pass.
6. Update the `Dockerfile`'s CACHE ORDERING comment and `tasks/reference/` if a doc describes the
   layer order.

## Decisions

William Emerison Six <billsix@gmail.com>, 2026-11-04 ("1 yes, 2 yes, wait until I say go"):

1. **Order:** do this task before the offline-pyright change, so that change doesn't re-download
   Mathlib.
2. **Toolchain:** `install-lean.sh` installs the toolchain pinned in `proofs/lean-toolchain`, not
   `stable` (plan step 3 is in scope).
3. **Timing:** start only when the maintainer says go (they are rebuilding the image outside the
   sandbox).
