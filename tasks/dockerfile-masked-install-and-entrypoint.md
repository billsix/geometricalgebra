# Dockerfile: fail on a failed base install, ship the entrypoint, fix stale comments

**Status:** proposed — needs go-ahead (approved in session 2026-11-09; in progress)
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.1

## BLUF

Done means:

- a failing `01-install-base.sh` fails `make image`;
- the image starts without a `--entrypoint` override;
- `make image` no longer bind-mounts the vendored Emacs tree into the build;
- the stale comments and script headers in the image/entrypoint files say what is true.

## Context

All re-checked on 2026-11-09.

- **The masked base install.** `Dockerfile` runs `/usr/local/bin/01-install-base.sh ;` then the
  optional groups with `;`. The `RUN`'s status is the final `uv pip install`'s, so a failed base
  install is masked. The template convention is to dispatch group scripts with `&&`.
- **The missing entrypoint.** `ENTRYPOINT ["/entrypoint.sh"]` names a file that is only bind-mounted
  (`FILES_TO_MOUNT`), never `COPY`'d. So a bare `podman run gacalc` fails, although the Dockerfile
  bakes the source for exactly that non-mounted use.
- **The elpa mount on the build.** `make image` passes `$(ELPA_MOUNT)` to `podman build`. With the
  default `USE_EMACS=1` that bind-mounts `entrypoint/dotfiles/.emacs.d/elpa` into the build with
  `:U`, which can chown the host tree. No build step reads it: the packages are never baked, and
  `.dockerignore` excludes them. The comment above `ELPA_MOUNT` says "Default is off", which went
  stale when `USE_EMACS` became `?= … 1`.
- **Stale comments:**
  - `Dockerfile:8-10`: "lean when built nested". Since 2026-09-27, nested builds are full unless
    `MINIMAL_IMAGE=1`.
  - `Dockerfile:186`: "dnf/MELPA/TeX". MELPA is not baked.
  - `entrypoint/05-install-emacs.sh`: "skips it in a lean nested image".
  - `entrypoint/03-install-notebook-tex.sh`: "Always installed … unconditionally". It is gated on
    `USE_JUPYTER || BUILD_DOCS`.
  - `entrypoint/jupyter.sh` and `shell.sh`: "(scalar/g1/g2/g3.py)". There is no `scalar.py`.
  - `pyproject.toml`'s licence comment: `gacalc.g2.Vector2`, now `Vector`.
- **Script modes and shebangs:**
  - `entrypoint/docs.sh` is `100644`;
  - `docs.sh`, `entrypoint.sh`, `format.sh` and `percentToIpynb.sh` use `#!/bin/env bash`, which is
    not present on every host;
  - `shell.sh`, `jupyter.sh` and `spyder.sh` have no shebang.
- **Not changed:**
  - `spyder.sh` and `percentToIpynb.sh` look vestigial (no target runs them), but the maintainer may
    use them by hand. They stay, and the done-record notes it.
  - The image's unpinned dependencies are a separate optional follow-up (§8.1).

## Plan

- [ ] Chain the base RUN with `&&` (the `if` blocks return 0 when their flag is off).
- [ ] `COPY entrypoint/entrypoint.sh /entrypoint.sh` before `ENTRYPOINT`.
- [ ] Drop `$(ELPA_MOUNT)` from the `image` recipe, and correct the `ELPA_MOUNT` comment.
- [ ] Fix the comments listed above.
- [ ] Use `#!/usr/bin/env bash` throughout; add shebangs where missing; `docs.sh` +x.
- [ ] Verify:
  - `make image MINIMAL_IMAGE=1`;
  - `podman run --rm gacalc -c 'echo ok'` with no `--entrypoint`;
  - a shell check that a failing first command now fails the chain;
  - `make test MINIMAL_IMAGE=1`.

## Open questions

None.
