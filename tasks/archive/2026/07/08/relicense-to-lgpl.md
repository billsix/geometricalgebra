# Relicense gacalc from GPL v2+ to LGPL

**Created:** 2026-07-08 · **Completed:** 2026-07-08

gacalc's license was changed from GPL v2+ to the LGPL, authorized by the maintainer ("go ahead and
do the relicense to LGPL task").

The request came out of modelviewprojection's `ctc-vector2-deferral` work
(github.com/billsix/modelviewprojection `tasks/archive/2026/07/08/ctc-vector2-deferral.md`): the shim
(`pgzero_gl`) is LGPL-2.1-only and its `Vector2` work-alike subclasses `gacalc.g2.Vector2`, so an
LGPL gacalc makes the coupling license-clean.

## What was done

- **Authorship verified**: `git log` showed a single author across all 239 commits (William Emerison
  Six), so the relicense was the maintainer's alone to make.
- **License chosen: `LGPL-2.1-only`**, matching pgzero_gl exactly (the task's recommended option; the
  maintainer's "go ahead" was taken as accepting it).
- **`LICENSE`** was replaced: a gacalc preamble (source LGPL-2.1-only, docs GFDL 1.3, preserving the
  old file's docs-license note) plus the full LGPL-2.1 text (pygame's copy, the same source pgzero_gl
  vendored).
- **Per-file headers**: every project `.py` (src/gacalc, tools, tests, notebooks) got
  `SPDX-License-Identifier: LGPL-2.1-only` plus a compact LGPL notice, replacing the 14-line GPL-2+
  block. That included the generator's two emitted-header strings in `tools/gen_specialized.py`
  (`header()` + `SCALAR_HEADER`), so the gitignored generated `g1/g2/g3/scalar.py` regenerate with the
  new header. `setup.py` never had a license header and was left as is; the vendored elpa tree
  (third-party) was untouched.
- **`pyproject.toml`**: PEP 639 `license = "LGPL-2.1-only"` + `license-files = ["LICENSE"]` were added
  (there was no license field before).
- **`README.md`** License section and the **`CLAUDE.md`** packaging note were updated to LGPL-2.1-only.

## Verification (2026-07-08, in container)

- `grep -ri GPL` over `*.py`/`*.toml`/`*.md` (excluding elpa) found only LGPL, apart from historical
  mentions inside `tasks/archive/` docs.
- `make test`: 253 passed; `make check-generated`: deterministic; `make format`: ruff + ty clean.
- `make dist`: the wheel METADATA showed `License-Expression: LGPL-2.1-only`, `License-File: LICENSE`
  bundled under `dist-info/licenses/`, and the baked generated modules carried the SPDX header.

## Release note

Already-published PyPI versions (≤0.0.5) keep their GPL grant; the relicense applies from the next
release, which also shipped the subclass-preserving ops fix mvp's Vector2 shim needed
(`tasks/archive/2026/07/08/subclass-preserving-generated-ops.md`).
