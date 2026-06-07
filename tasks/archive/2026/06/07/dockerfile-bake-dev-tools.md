# Bake the `dev` extras (build, twine) into the image via a source COPY

**Status:** complete
**Started:** 2026-06-07
**Completed:** 2026-06-07

## Goal

Make `make shell` (i.e. the container image) carry the publish tooling — `build` + `twine` — so
`make dist` / `make upload` / `make release` work inside the container with **no per-shell network
fetch**, and do it from the **single source of truth**: the `[project.optional-dependencies] dev`
group in `pyproject.toml` (not a hardcoded `build twine` list).

This replaces the interim `RUN uv pip install --system build twine` (which hardcoded the two names
because `pyproject.toml` wasn't in the image at build time).

## Key idea (from the author)

If the Dockerfile **copies the project source into the image**, then `pyproject.toml` is present at
build time, so the build can `pip install ".[dev]"` and pull the dev tools from the extras group. At
runtime, `make shell`'s bind mount (`-v $(pwd):/geometricalgebra/:Z`) **overlays** that baked-in copy
with the live host tree — so the copy is only used for the build; development still happens against
live files. Both halves verified correct.

## Design decision: targeted COPY, not literal `COPY .`

Literal `COPY . /geometricalgebra` would **duplicate the 31M vendored Emacs `elpa` tree** (it lives
under `entrypoint/dotfiles/.emacs.d/elpa`, already `COPY`'d to `/root`) into `/geometricalgebra`. A
`.dockerignore` **cannot** fix this: it filters the build context *globally*, so excluding the elpa
tree would also break the `COPY entrypoint/dotfiles/ /root/` that legitimately needs it (and the
vendored tree is intentional / off-limits per CLAUDE.md).

So we copy only the build-relevant files (~700K), which is also better for layer caching (only a change
to these busts the install layer, not e.g. a notebook or task-doc edit):

```dockerfile
COPY pyproject.toml setup.py requirements.txt README.md /geometricalgebra/
COPY src   /geometricalgebra/src
COPY tools /geometricalgebra/tools
RUN cd /geometricalgebra && uv pip install --system --no-build-isolation ".[dev]"
```

- Placed **after** the slow `dnf`/MELPA/`requirements.txt` layers, so source edits don't re-run those.
- `--no-build-isolation` reuses the already-installed `setuptools`/`wheel`/`numpy`/`sympy` (from the
  big RUN) instead of spinning up an isolated build env to re-download them.
- Runtime deps are already installed, so this step mainly fetches `build`+`twine`; the `build_py` hook
  generates the specialized algebras if missing (they're copied in, so it no-ops).
- Bonus: the image becomes partially self-contained (the package is installed from real source), though
  not fully runnable without the mount since `tests/`/`Makefile`/`notebooks/` aren't copied.

## `.dockerignore`

Trims the build context (the elpa tree must stay for the `/root` copy, but caches/artifacts/`.git`
can go):

```
.git
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
*.egg-info/
build/
dist/
.ipynb_checkpoints/
```

## Plan

- [x] Add `.dockerignore`.
- [x] Dockerfile: remove the interim `RUN uv pip install --system build twine`; add the targeted
      `COPY`s + `RUN ... ".[dev]"` after the big layer.
- [x] Free space + rebuild fresh. The graphroot is an **8G tmpfs**; the image is 3.6G, so two copies
      don't fit — the earlier in-place rebuild died with `no space left on device`. Removed the old
      image first (tmpfs 3.5G→185M used), then rebuilt clean (exit 0, image 3.62G).
- [x] Verify `build`+`twine` import inside the rebuilt image; `geometricalgebra` imports; overlay works.

## Verified (2026-06-07)

- Rebuilt image imports `build` 1.5.0 + `twine` 6.2.0, and `from geometricalgebra.g2 import G2`
  works **without the bind mount** (installed from the COPY'd source — the self-contained bonus). ✅
- **Overlay confirmed:** with `-v $(pwd):/geometricalgebra:Z`, `Makefile` + `tests/` (which are *not*
  in the image's COPY) are visible inside the container — the live host tree shadows the baked copy. ✅
- **In-container publish workflow:** `make dist` builds sdist+wheel and `twine check` PASSES *inside*
  the container, using the baked-in dev tools. ✅

## Notes

- Cross-ref `tasks/build-time-codegen-dist.md` (defines the `dev` extras and the `make dist`/`release`
  targets this feeds). `shell.sh` still runs the generator + editable install at runtime over the
  overlaid tree — unchanged.
- The `make shell` `podman run` still lacks `--cgroups=disabled` (needed only to run *nested* in the
  Claude sandbox); orthogonal, not changed here.
