# gacalc: structural venv consistency with mvp

**Completed:** 2026-06-14 (directed by the maintainer; verified on the rebuilt image)

## Why

On the real full image, `ty check` reported 3 `unresolved-import`s
(`IPython`, `IPython.display`, `matplotlib_inline.backend_inline`). Root cause:
gacalc has **no venv** — it installs `uv pip install --system`, which on Fedora
splits deps across two prefixes:

- dnf packages (pytest, ruff, ty, numpy) → `/usr/lib(64)/.../site-packages`
- `uv pip --system` packages (IPython, matplotlib_inline, sympy) → `/usr/local/lib(64)/...`

ty's default detection uses `sys.prefix=/usr` and searches only `/usr/lib(64)`,
so it never sees the `/usr/local` half. mvp doesn't have this problem because it
builds a **`--system-site-packages` venv** and every script/target activates it,
so ty keys off `VIRTUAL_ENV` and resolves everything.

A stopgap (`--extra-search-path /usr/local/...` in `format.sh`) worked, but the maintainer
wanted gacalc structurally consistent with mvp instead. (It also fixes a latent
bug: `percentToIpynb.sh` already `source`s `/venv/bin/activate`, a `/venv` that
didn't exist.)

## What was done (mirroring mvp exactly)

mvp's idiom: every entrypoint script begins
`export VIRTUAL_ENV_DISABLE_PROMPT=1; source /venv/bin/activate`; deps are
`uv pip install --python $(which python)` into the activated venv; `which` is a
dnf package.

1. **Dockerfile**
   - added `which` to the dnf install list (needed for `$(which python)`).
   - first RUN: creates `python3 -m venv --system-site-packages /venv/`, activates
     it, and installs setuptools/wheel/numpy/sympy + pyright into it (no `--system`).
   - second RUN: re-activates `/venv` (env doesn't persist across RUN) and installs
     `.[dev,notebooks,jupyter]` into it (no `--system`).
2. **entrypoint scripts** — the activate idiom was prepended to `shell.sh`,
   `jupyter.sh`, `spyder.sh`, `entrypoint.sh`, `format.sh`; shell.sh's editable
   install switched to `--python $(which python)`; `percentToIpynb.sh` already
   activated (the DISABLE_PROMPT export was added for uniformity).
3. **format.sh** — the `--extra-search-path` stopgap was reverted (the venv makes ty
   find everything).
4. **Makefile** — the containerized `format` / `test` / `dist` recipes ran
   `python` directly; `source /venv/bin/activate;` was prepended to each. (`generate` /
   `check-generated` / the `VERSION :=` shell-out run on the host and were left.)

## Verification (2026-06-14, rebuilt image)

- `make format` → 3× "All checks passed!" with **no flags** in format.sh.
- `make test` → **225 passed**.
- `sys.prefix` = `/venv`; IPython/numpy/gacalc resolve from `/venv/lib64/...`.

## Notes

- CLAUDE.md needed no edit — it made no `--system`/install-location claim that
  the venv change falsifies (the "ty fully clean, no ty.toml/override" claim is
  now true more cleanly: the `--extra-search-path` stopgap was removed).
- Files changed: `Dockerfile` (+which, venv in both RUNs), `Makefile`
  (activate in format/test/dist), `entrypoint/{shell,jupyter,spyder,entrypoint,
  percentToIpynb,format}.sh`. `percentToIpynb.sh`'s pre-existing `source
  /venv/...` (a `/venv` that never existed) now works.
