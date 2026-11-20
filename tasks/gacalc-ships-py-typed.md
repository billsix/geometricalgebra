# gacalc ships a `py.typed` marker

**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>) · **Done:** 2026-11-20

gacalc's code was fully annotated, but without the PEP 561 marker a consumer's mypy ignored those
annotations. Found while separating out the ePiX type problem
(`tasks/archive/2026/11/19/notebooks-one-directory.md`); the shared rule is runClaudeInContainer's
`tasks/python-packages-ship-type-information.md` (github.com/billsix/runClaudeInContainer).

## What was done

- Added an empty `src/gacalc/py.typed`, plus `"gacalc" = ["py.typed"]` in `pyproject.toml`'s
  `[tool.setuptools.package-data]`. The marker covers every subpackage, `gacalc.epixscene` included
  (ePiX ships its own types since epix-mirror `33d0194`).
- Added a `CHANGELOG.md` `[Unreleased]` "Added" entry: a consumer's checker now reads gacalc's
  annotations, which can surface new errors in their code. Also a one-line note in `CLAUDE.md`'s
  Packaging bullet.

## Verification

- `python -m build --no-isolation` in the `gacalc` image, with the default dims 1–3 instead of
  `make dist`'s 1–5, because the marker does not depend on which dims are generated. The wheel
  lists `gacalc/py.typed`; the sdist has `gacalc-0.1.1/src/gacalc/py.typed`.
- Consumer check: a fresh venv with the wheel, numpy, sympy and mypy installed, checking
  `from gacalc.g2 import e_1; reveal_type(3 * e_1)`:
  - mypy: `Revealed type is "gacalc.g2.Vector"`, no issues.
  - pyright (the image's): `Type of "3 * e_1" is "Vector"`.
  - mypy with the marker deleted from site-packages: `import-untyped` error and `Any`. So the
    marker is what makes the difference.
- `entrypoint/format.sh` exited 0.
