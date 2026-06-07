# Document (and reconcile) the Emacs-package vendoring workflow

**Status:** complete — documented the workflow, excluded elpa from the image build, dropped the
build-time install, and added `make update-emacs-packages` (wipe+reinstall, strip *.elc/*.eln, git
add -f). All open questions resolved.
**Started:** 2026-06-07
**Completed:** 2026-06-07

## Also done (2026-06-07) — partial scope 3: stop baking the vendored tree into the image

Per the author's request, added `entrypoint/dotfiles/.emacs.d/elpa` to `.dockerignore`, so the vendored
package tree is **no longer copied into the image** (`COPY entrypoint/dotfiles/ /root/` now skips it).
The `.emacs.d` config (`init.el`, `install-melpa-packages.el`, `helm.el`, `preferences.el`) is still
copied, so the build's `emacs --batch --load .../install-melpa-packages.el` step still runs and is now
what populates the image's packages. The tree stays vendored in git for the `USE_EMACS=1` workflow.

Verified with a throwaway `COPY entrypoint/dotfiles/ /root/` build: `/root/.emacs.d` contains the four
config `.el` files and **no** `elpa/`.

Note: `.dockerignore` ≠ `.gitignore` — the CLAUDE.md off-limits rule (which forbids *gitignoring* the
tree) is preserved; the tree remains tracked in git. (Author confirmed "for this context only it's
fine" to work on this.)

### Final design (author-clarified 2026-06-07)

The image no longer carries Emacs packages at all; the vendored git tree is the source, used at
runtime via mount. Concretely:

- **Dockerfile:** removed the build-time `emacs --batch --load .../install-melpa-packages.el` step. The
  build neither copies (`.dockerignore`) nor installs the packages. The `.emacs.d` *config* (init.el,
  install-melpa-packages.el, …) is still copied.
- **New `make update-emacs-packages` target:** the "easy way" to refresh + vendor. Steps (per author
  request 2026-06-07):
  1. `$(MAKE) image USE_EMACS=1` — rebuild the image first (covers "the last build didn't set
     USE_EMACS"). NB: after removing the build-time install, `USE_EMACS` no longer changes the image
     build, so this is harmless belt-and-suspenders. The elpa mount is hardcoded inline in the target
     (not the `USE_EMACS`-gated `ELPA_MOUNT`), so the target always mounts regardless.
  2. In the container: `find /root/.emacs.d/elpa -mindepth 1 -delete` then `emacs --batch --load
     install-melpa-packages.el` (elpa bind-mounted RW; install script mounted RO so edits apply without
     a rebuild) — fresh packages land on the host tree.
  3. On the host, in the elpa dir: `find . \( -iname '*.elc' -o -iname '*.eln' \) -delete` (drop
     compiled byte/native lisp — both are regenerated, machine-specific build artifacts) then
     `git add -A -f .` (`-f` overrides `.gitignore`'s `*.elc`/`*.eln`/… so the full tree stages).
  Verified it parses + dry-runs; **not executed** (it would rebuild the image and rewrite the 31M
  vendored tree — author runs + commits that deliberately).

Resolved questions (2026-06-07):
- **`*.eln`:** strip it too (author confirmed). `.eln` = natively-compiled elisp (Emacs 28+
  libgccjit), the native-code analogue of `.elc` bytecode — arch/version-specific, regenerated. Now
  stripped alongside `.elc`. (Note: native-comp usually writes `.eln` to a separate `eln-cache/`, not
  into `elpa/`, so the strip may be a no-op there — harmless.)
- **Image-rebuild first step (b):** kept `$(MAKE) image USE_EMACS=1` as the target's first step. It
  guards against a missing/stale image and is fast when layers are cached; the `USE_EMACS=1` part is
  cosmetic now (post-removal of the build-time install it doesn't change the image) but kept as
  requested and as future-proofing.
- **`make shell USE_EMACS=1`:** unchanged — mounts the vendored tree so an interactive session *uses*
  the packages. Default `USE_EMACS=0` = no mount.
- **Docs:** README "Updating the vendored Emacs packages" + the `ELPA_MOUNT` Makefile comment rewritten
  to point at `make update-emacs-packages` and the use-vs-refresh split.

Reproducibility now lives entirely in the vendored git tree (refreshed deliberately via
`make update-emacs-packages`, committed), not in any build-time fetch — the build is now offline w.r.t.
Emacs packages.

## Done (2026-06-07) — scope 1, document only

Documented the `make shell USE_EMACS=1` → `install-melpa-packages` → commit-the-tree vendoring loop in
two places: a comment block above `ELPA_MOUNT` in the `Makefile` (at the mechanism), and an "Updating
the vendored Emacs packages" subsection under `## Develop` in `README.md`. No behavior change; the
`elpa/` tree contents were not touched. Scopes 2 (a `make update-emacs-packages` target) and 3
(reconcile with the Dockerfile build-time install) were **not** done — left below if ever wanted.

## What the author was looking for (now found)

The author set up a workflow where `make shell` mounts the host's Emacs `elpa` directory into the
container so that, inside, `install-melpa-packages` writes packages **back to the host**, which are
then committed (vendored) from outside the container. The author couldn't find it and asked whether it
still exists. **It does** — but it's gated and undocumented, which is why it was lost.

## The mechanism (verified, build-mechanics only — not the off-limits `elpa/` contents)

- `Makefile:4` — `USE_EMACS ?= 0` (default **off**).
- `Makefile:46-50` — when `USE_EMACS=1`:
  `ELPA_MOUNT = -v $(CURDIR)/entrypoint/dotfiles/.emacs.d/elpa:/root/.emacs.d/elpa:U,z`
- `Makefile:73` — `make shell` injects `$(ELPA_MOUNT)` into the `podman run` (also `Makefile:60` for
  `make image`).
- `:U` recursively chowns the mount to the container user; `:z` is the SELinux shared relabel — together
  they make the bind mount writable from inside, so installed packages persist to the host dir.

So the intended flow is:

```
make shell USE_EMACS=1     # bind-mounts host elpa -> /root/.emacs.d/elpa (writable)
#   in container: emacs install-melpa-packages  -> writes to the host elpa tree
#   outside:      git commit the updated elpa tree   (vendored)
```

With the default `USE_EMACS=0`, `ELPA_MOUNT` is empty, so packages installed in-container go to the
container's **ephemeral** `/root/.emacs.d/elpa` and are lost on `--rm` — nothing is written back. That
is why the workflow "wasn't happening" / couldn't be found.

## The real gap

The workflow is correct but **invisible**: no doc mentions `USE_EMACS=1` or the update-then-vendor
loop, so it's easy to forget it exists (it was). Likely goal: **document it** so it's discoverable.

## Possible scope (pick one — needs go-ahead)

1. **Document only (recommended).** Add a short "Updating the vendored Emacs packages" note — where?
   Candidates: `README.md`, a comment block near `ELPA_MOUNT` in the `Makefile`, or a dedicated
   `entrypoint/README` . Spell out `make shell USE_EMACS=1` → `install-melpa-packages` → commit.
   - Caveat: `CLAUDE.md` marks the `elpa/` *tree* off-limits, but documenting the *workflow/Makefile
     knob* is build-mechanics, not touching the tree. Confirm the author is OK with a doc that
     references the vendored tree's update path.
2. **Document + ergonomics.** Add a convenience target, e.g. `make update-emacs-packages` =
   `make shell USE_EMACS=1` wired to run the install non-interactively, so vendoring is one command.
3. **Reconcile with the build-time install.** Separately, the Dockerfile *also* runs
   `emacs --batch --load .../install-melpa-packages.el` at **build** (Dockerfile:32) while the tree is
   already vendored — clarify whether that build-step is needed given the vendored tree, or is
   redundant. (This is the "ship twice?" question from the earlier draft.) Only if the author wants to
   touch it.

## Open questions

- Is scope #1 (document) all you want, or also #2 / #3?
- Where should the doc live?
- Does the off-limits rule on the `elpa/` tree extend to *documenting how to update it*? (I read: no —
  the rule is about not reading/editing the tree's *contents*; a workflow note is fine — but confirm.)
