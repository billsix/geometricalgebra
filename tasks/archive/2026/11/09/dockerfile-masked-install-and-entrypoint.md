# Dockerfile: fail on a failed base install, ship a working entrypoint, fix stale comments

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §8.1

## What was wrong

- **The masked base install.** The base-install `RUN` chained `01-install-base.sh ;` and the optional
  groups with `;`, so a failed base install didn't fail the build. The `RUN`'s status was the final
  `uv pip install`'s.
- **The entrypoint.** `ENTRYPOINT ["/entrypoint.sh"]` named a file that was only bind-mounted, never
  baked, so a bare `podman run gacalc` couldn't start. Once baked, a second bug showed: it ended in
  `exec bash` without `"$@"`, so `podman run gacalc -c '…'` silently ignored the command and exited 0.
  (Found while verifying this task.)
- **The elpa mount on the build.** `make image` passed `$(ELPA_MOUNT)` to `podman build`, which
  bind-mounted the vendored Emacs tree into every default build with `:U`. No build step reads it.
  Its comment said "Default is off".
- **Stale comments:**
  - `Dockerfile` said flags are "lean when built nested";
  - `Dockerfile` listed "dnf/MELPA/TeX";
  - `05-install-emacs.sh` said "a lean nested image";
  - `03-install-notebook-tex.sh` said "Always installed … unconditionally";
  - `shell.sh` and `jupyter.sh` mentioned a `scalar.py`;
  - `pyproject.toml` cited `gacalc.g2.Vector2`.
- **Script modes and shebangs:** `docs.sh` was `100644`; four scripts used `#!/bin/env bash`; three
  had no shebang.

## What changed

- **`Dockerfile`:**
  - the base `RUN` dispatches with `&&` (the `if … fi` blocks return 0 when a flag is off, so only a
    real failure stops the chain);
  - `COPY entrypoint/entrypoint.sh /entrypoint.sh` before `ENTRYPOINT`, with a comment that the
    Makefile's bind mount still overrides it;
  - the two stale comments fixed.
- **`entrypoint/entrypoint.sh`** ends `exec bash "$@"`: an interactive shell with no arguments, and
  the given command otherwise.
- **`Makefile`:** `$(ELPA_MOUNT)` is gone from the `image` recipe, and its comment now says the mount
  serves the `shell`/`shell-exec`/`jupyter` containers, not the build.
- **Comments:** `05-install-emacs.sh`, `03-install-notebook-tex.sh` (reflowed), `shell.sh`,
  `jupyter.sh`, `pyproject.toml`.
- **Shebangs and modes:** `#!/usr/bin/env bash` throughout, added to `shell.sh`/`jupyter.sh`/
  `spyder.sh`; `docs.sh` is `100755`.
- **Left alone on purpose:** `spyder.sh` and `percentToIpynb.sh` look vestigial (no target runs
  them), but they may be used by hand.

## Verification

- `bash -n` on every `entrypoint/*.sh`: clean. Every script is `100755`.
- The chain shape: `false && if [ 0 = 1 ]; then …; fi && echo reached` exits 1 without printing, so a
  failed first command fails the chain.
- `make image MINIMAL_IMAGE=1` (nested): built. `podman image inspect gacalc` shows the
  `/entrypoint.sh` entrypoint.
- `podman run --rm gacalc -c 'echo entrypoint-ok; python -c "import gacalc.g2; …"'`, with no
  `--entrypoint`, prints `entrypoint-ok` and `e_1`'s repr.
- `make test MINIMAL_IMAGE=1`: 752 passed, 2 skipped.
