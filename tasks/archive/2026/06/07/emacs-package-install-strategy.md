# Document (and reconcile) the Emacs-package vendoring workflow

**Created:** 2026-06-07 · **Completed:** 2026-06-07

## The workflow that had been lost

The author had set up a flow where `make shell` mounts the host's Emacs `elpa` directory into the
container so that `install-melpa-packages` writes packages back to the host, to be committed (vendored)
from outside. The author could not find it. It still existed, but was gated and undocumented:

- `Makefile` — `USE_EMACS ?= 0` (off by default); when `USE_EMACS=1`,
  `ELPA_MOUNT = -v $(CURDIR)/entrypoint/dotfiles/.emacs.d/elpa:/root/.emacs.d/elpa:U,z`, injected into
  the `make shell` (and `make image`) `podman run`. `:U` chowns the mount to the container user and `:z`
  relabels it for SELinux, so it is writable from inside.
- With the default `USE_EMACS=0` the mount was empty, so packages installed in-container went to the
  ephemeral `/root/.emacs.d/elpa` and vanished on `--rm` — why the workflow "wasn't happening".

## What was done (2026-06-07)

1. **Documented** the `make shell USE_EMACS=1` → `install-melpa-packages` → commit loop in a comment
   block above `ELPA_MOUNT` in the `Makefile` and an "Updating the vendored Emacs packages" subsection
   under `## Develop` in `README.md`. A dedicated `entrypoint/README` was considered as the location but
   not written (it does not exist). The decision on scope: documenting the workflow is build mechanics,
   not touching the off-limits `elpa/` contents, so the CLAUDE.md rule did not forbid it.
2. **Stopped baking the vendored tree into the image.** `entrypoint/dotfiles/.emacs.d/elpa` was added to
   `.dockerignore`, so `COPY entrypoint/dotfiles/ /root/` skips it while still copying the config
   (`init.el`, `install-melpa-packages.el`, `helm.el`, `preferences.el`). A throwaway build confirmed
   `/root/.emacs.d` held the four config files and no `elpa/`. `.dockerignore` is not `.gitignore`: the
   tree stayed tracked in git, so the CLAUDE.md rule against gitignoring it was kept (the author
   confirmed "for this context only it's fine" to work on this).
3. **Dropped the build-time install** (author-clarified final design): the Dockerfile's
   `emacs --batch --load .../install-melpa-packages.el` step was removed, so the image carries no Emacs
   packages; the vendored git tree is the source, used at runtime via the mount. The build became
   offline with respect to Emacs packages.
4. **Added `make update-emacs-packages`**, the one-command refresh:
   1. `$(MAKE) image USE_EMACS=1` first, guarding against a missing or stale image (fast when cached;
      the `USE_EMACS=1` part became cosmetic once the build-time install was gone, and was kept as
      requested). The elpa mount is hardcoded in the target, not the `USE_EMACS`-gated `ELPA_MOUNT`.
   2. In the container: `find /root/.emacs.d/elpa -mindepth 1 -delete`, then
      `emacs --batch --load install-melpa-packages.el` (elpa mounted read-write, the install script
      read-only so edits apply without a rebuild).
   3. On the host in the elpa dir: delete `*.elc` and `*.eln`, then `git add -A -f .` (`-f` overrides
      `.gitignore`'s `*.elc`/`*.eln`).

   It was verified to parse and dry-run, but not executed: it rebuilds the image and rewrites the 31M
   vendored tree, which the author runs and commits deliberately.

## Decisions (2026-06-07)

- **Strip `*.eln` too** (author confirmed): natively-compiled elisp (Emacs 28+ libgccjit) is
  arch/version-specific and regenerated. Native-comp usually writes to a separate `eln-cache/`, so the
  strip may be a no-op there.
- `make shell USE_EMACS=1` stayed as is (mounts the tree so a session uses the packages); the default
  `USE_EMACS=0` mounts nothing.
- README "Updating the vendored Emacs packages" and the `ELPA_MOUNT` comment were rewritten to point at
  `make update-emacs-packages` and the use-vs-refresh split.

Reproducibility lives entirely in the vendored git tree, refreshed deliberately and committed.
