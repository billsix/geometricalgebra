# Let pyright check the live-figure notebooks once ePiX ships type information

**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>), split off from
`tasks/archive/2026/11/19/notebooks-one-directory.md`.
**Done:** 2026-11-19, branch `epix-type-stubs-for-pyright` (`ac90d6b`).

pyright had excluded the 31 notebooks that draw live ePiX figures, and ty allowed `epix` to be
unresolved, because ePiX shipped no type information and its editable install hid it from static
checkers. epix-mirror now ships `py.typed` and a generated `_epix.pyi` (`33d0194`, its
`tasks/archive/2026/11/19/ship-python-type-information.md`). Both checkers now check every
notebook and `gacalc.epixscene`, in the full image and in CI's lean one. The resulting state is
in `tasks/reference/demo-and-book-notebooks.md` ("ePiX and the type checkers").

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-19)

- Once epix shipped stubs, the excludes go entirely; none of the list is kept.
- **The lean image gets epix's types by copying its typed sources.** Building ePiX in CI was
  declined, since every run would pay for meson, g++, ghostscript, ImageMagick and three TeX Live
  collections. So was keeping the allowances in CI.

## What was done

- `Dockerfile`: `EPIX_COMMIT` moves from `797b944` to `33d0194`. The only changes between the two
  are the type annotations in `figure.py` and `render.py` and the new stub; no C++ or binding
  source changed. With `USE_EPIX=0`, the ePiX step now runs `entrypoint/install-epix-stubs.sh`.
- `entrypoint/install-epix-stubs.sh` (new) fetches `__init__.py`, `figure.py`, `render.py` and
  `_epix.pyi` at `EPIX_COMMIT` from raw.githubusercontent.com. It installs them as
  `site-packages/epix-stubs/*.pyi`, a PEP 561 stub-only package: checkers read it, and
  `import epix` still fails, so the root `conftest.py` still skips `gacalc.epixscene`.
- `entrypoint/install-epix.sh` installs epix editable with
  `--config-settings editable_mode=compat`, a plain path `.pth`. It runs `build_py.sh` with
  `PYTHONPATH="$SRC/python"`, because that script's new stubgen step imports `epix._epix` before
  the package is installed. The first full-image build failed there (exit 2,
  `ModuleNotFoundError: No module named 'epix'`). The fix that belongs upstream, in epix-mirror's
  `build_py.sh`, is noted below.
- `pyrightconfig.json` lost its 31-notebook `exclude` list. `pyproject.toml` lost
  `[tool.ty.analysis] allowed-unresolved-imports`.
- `notebooks/frame-qr-2d.py`: sympy types `Matrix[i, j]` and `Matrix[:2, :2]` as
  `MatrixElement | list`, which pyright rejected for a `Real` or `sympy.Matrix` binding. The
  notebook now reads the block with `.extract([0, 1], [0, 1])` and the entry with
  `table.row(1)[0]`, and its outputs are unchanged.
- The CI comment in `.github/workflows/checks.yml`, `CLAUDE.md` (`make check-notebooks`), and the
  two reference docs describe the result.

## Verification

- **Lean image** (`make image MINIMAL_IMAGE=1`, tagged `gacalc-lean` for the test, 3.4 GB):
  `import epix` fails and the four stubs are installed. `make format` exited 0, `pyright
  notebooks/` reported 0 errors, and `make test` passed (1393 passed, 3 skipped).
- **Full image:** epix is installed through a path `.pth`. `make format` exited 0, `pyright
  notebooks/` reported 0 errors, and `check_annotations.py` gave 63 findings, the same as master.
  The stub the image build wrote is byte-identical to epix-mirror's committed one.
- The 49 prebuilt figures' eepic is identical to this session's baseline. `frame-qr-2d` and
  `vector-addition` executed with outputs identical to before.

## Left for the maintainer

- **epix-mirror's `entrypoint/build_py.sh` assumes `epix` is importable** when it runs
  `nanobind.stubgen -m epix._epix`. That holds in epix-mirror's own image and failed in gacalc's
  build. The fix is to run that step with `PYTHONPATH=python`. gacalc works around it, and the
  workaround stays harmless once the upstream fix lands.
