# Rename AbstractMultiVector -> MultiVectorBase

**Created:** 2026-06-11 · **Completed:** 2026-06-12

## What was done (2026-06-12)

- **Hard rename** (the maintainer's call) — no deprecated `AbstractMultiVector = MultiVectorBase`
  alias. The name appeared in notebooks and was importable, so this was a small breaking change,
  accepted because the repo was solo/pre-1.0.
- Swept the bare token `AbstractMultiVector → MultiVectorBase` across all 8
  hand-written files (115 occurrences): `base.py` (51, incl. the `_OperandT`
  bound), `transforms.py` (24), `nbplotutils.py` (21), `gn.py` (6),
  `tools/gen_specialized.py` (10), `tools/astbuild.py` (1), and the two notebook
  prose references (`displayrotations.py`, `displaygraded.py`). The change is in the
  **generator**, not the generated output — `make generate` re-emitted
  `g1/g2/g3.py` + `scalar.py` with the new name (the 15 generated occurrences).
- Docs updated to match: `README.md` (1) + `CLAUDE.md` (7).
- **Import sorting:** the rename reordered `from gacalc.base import ...` (M now sorts
  after B/C); `ruff --fix` resorted the 2 affected source imports, and the generator
  post-formats its own output so a fresh `make generate` stays ruff-clean.
- **Left as historical record:** archived task docs under `tasks/archive/` (they
  genuinely referred to the old name at the time). The two *live* forward-looking
  task docs (`generalize-sandwich-other-grades`, `generalize-reject-reflect-higher-grade`)
  were updated to the new name.
- **Verify:** `ty` clean · `ruff` clean (after a fresh generate) · determinism
  (`gen_specialized.py` twice → identical) · **221 passed** · notebooks
  `displaygraded`/`displayrotations` execute headless. Unrelated aliases untouched
  (`MultiVector = Gn`, `MultiVectorFn`).

## Scope (measured 2026-06-11)

130 occurrences across 13 files (`grep -rn AbstractMultiVector src tools tests notebooks`): the
hand-written source, the generator (`tools/gen_specialized.py` and `tools/astbuild.py` emit the name
into the generated modules' class bases and `from gacalc.base import ...` header, so the rename was
made there and `make generate` re-emitted it), the gitignored generated modules, the notebooks, and a
regenerated `PKG-INFO` (ignored). It was done as a single sweep, minding the quoted string forms in the
generator versus the live class references in source.
