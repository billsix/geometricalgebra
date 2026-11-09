# Bake the `dev` extras (build, twine) into the image via a source COPY

**Created:** 2026-06-07 · **Completed:** 2026-06-07

## What changed

The container image now carries the publish tooling (`build` + `twine`), so `make dist` / `make upload`
/ `make release` work inside `make shell` with no per-shell network fetch. The tools come from the
single source of truth, the `[project.optional-dependencies] dev` group in `pyproject.toml`, replacing
the interim `RUN uv pip install --system build twine` that hardcoded the names because `pyproject.toml`
was not in the image at build time.

The author's idea: copy the project source into the image so `pyproject.toml` is present at build time
and the build can `pip install ".[dev]"`. At runtime `make shell`'s bind mount
(`-v $(pwd):/geometricalgebra/:Z`) overlays the baked copy with the live host tree, so the copy is used
only for the build.

## Decisions

- **Targeted `COPY`, not `COPY .`.** A literal `COPY .` would have duplicated the 31M vendored Emacs
  `elpa` tree (already copied to `/root` from `entrypoint/dotfiles/`) into `/geometricalgebra`, and a
  `.dockerignore` could not exclude it because it filters the context globally and would break the
  `/root` copy. Only the build-relevant files (~700K) were copied — `pyproject.toml setup.py
  requirements.txt README.md`, `src/`, `tools/` — which also keeps notebook or task-doc edits from
  busting the install layer.
- The `RUN cd /geometricalgebra && uv pip install --system --no-build-isolation ".[dev]"` layer was
  placed **after** the slow `dnf`/MELPA/`requirements.txt` layers; `--no-build-isolation` reuses the
  already-installed `setuptools`/`wheel`/`numpy`/`sympy`. The `build_py` hook no-ops because the
  generated algebras are copied in.
- A `.dockerignore` was added to trim the context (`.git`, `__pycache__/`, `*.py[cod]`,
  `.pytest_cache/`, `.ruff_cache/`, `*.egg-info/`, `build/`, `dist/`, `.ipynb_checkpoints/`).

The rebuild first died with `no space left on device`: the graphroot was an 8G tmpfs and the 3.6G image
did not fit twice. The old image was removed first (tmpfs 3.5G → 185M used), then the clean rebuild
succeeded (image 3.62G).

## Verification (2026-06-07)

- The rebuilt image imports `build` 1.5.0 and `twine` 6.2.0, and `from geometricalgebra.g2 import G2`
  works without the bind mount (installed from the copied source). `tests/`, `Makefile` and
  `notebooks/` were not copied, so the image is not fully runnable without the mount.
- With the mount, `Makefile` and `tests/` (absent from the image's copy) were visible in the container,
  confirming the live tree shadows the baked copy.
- `make dist` built sdist + wheel and `twine check` passed inside the container.

`shell.sh` still ran the generator and editable install at runtime, unchanged. Adding
`--cgroups=disabled` to the `make shell` `podman run` (needed only for nested runs) was left out as
orthogonal. Related: `tasks/archive/2026/06/07/build-time-codegen-dist.md` (defines the `dev` extras and
the `make dist`/`release` targets).
