# Relicense gacalc from GPL v2+ to LGPL

**Status:** DONE 2026-07-08 (authorized by Bill: "go ahead and do the
relicense to LGPL task"). Changes staged, uncommitted — Bill commits.
**Created:** 2026-07-09

## Goal (Bill)

Change gacalc's license from GPL v2+ to the LGPL.

## Context

Raised during modelviewprojection's `ctc-vector2-deferral` work: the shim
(`pgzero_gl`) is LGPL-2.1-only and its `Vector2` work-alike subclasses
`gacalc.g2.Vector2`; an LGPL gacalc makes the coupling license-clean.

## What was done

- **Authorship verified**: `git log` shows a single author across all 239
  commits (William Emerison Six) — relicensing is unilaterally Bill's.
- **License chosen: `LGPL-2.1-only`** — matches pgzero_gl exactly (the
  task's recommended option; Bill's "go ahead" taken as accepting it).
- **`LICENSE`** replaced: gacalc preamble (source LGPL-2.1-only, docs
  GFDL 1.3 — preserving the old file's docs-license note) + the full
  LGPL-2.1 text (pygame's copy, the same source pgzero_gl vendored).
- **Per-file headers**: every project `.py` (src/gacalc, tools, tests,
  notebooks) now carries `SPDX-License-Identifier: LGPL-2.1-only` plus a
  compact LGPL notice, replacing the 14-line GPL-2+ block. That includes
  the generator's two emitted-header strings in
  `tools/gen_specialized.py` (`header()` + `SCALAR_HEADER`), so the
  gitignored generated `g1/g2/g3/scalar.py` regenerate with the new
  header. `setup.py` never had a license header (left as is). The
  vendored elpa tree untouched (third-party).
- **`pyproject.toml`**: added PEP 639 `license = "LGPL-2.1-only"` +
  `license-files = ["LICENSE"]` (there was no license field before).
- **`README.md`** License section and **`CLAUDE.md`** packaging note
  updated to LGPL-2.1-only.

## Gates (all green, 2026-07-08, in container)

- `grep -ri GPL` over `*.py`/`*.toml`/`*.md` (excluding elpa): only LGPL
  remains, apart from historical mentions inside `tasks/archive/` docs
  and this file (the record, not live licensing).
- `make test` — 253 passed; `make check-generated` — deterministic;
  `make format` — ruff + ty all-checks-passed.
- `make dist` — wheel METADATA shows `License-Expression: LGPL-2.1-only`,
  `License-File: LICENSE` bundled under `dist-info/licenses/`, and the
  baked generated modules carry the SPDX header.

## Follow-up (Bill)

- Already-published PyPI versions (≤0.0.5) keep their GPL grant; the
  relicense applies from the next release. **Bump `version` in
  `pyproject.toml` before `make release`** — that release also ships the
  subclass-preserving ops fix mvp's Vector2 shim needs.
