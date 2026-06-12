# Rename AbstractMultiVector -> MultiVectorBase

Status: **DONE** · 2026-06-12 (hard rename, option a — no alias)

## What was done (2026-06-12)

- **Hard rename** (option a) — no deprecated alias; repo is solo/pre-1.0.
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

## Goal

Rename the abstract base class **`AbstractMultiVector` -> `MultiVectorBase`**
across the whole project.

## Scope (measured 2026-06-11)

**130 occurrences across 13 files** (`grep -rn AbstractMultiVector src tools tests
notebooks`):

- **Hand-written source:** `base.py` (the class definition + the `_OperandT`
  TypeVar `bound="AbstractMultiVector"` + many annotations), `gn.py`,
  `transforms.py`, `nbplotutils.py`.
- **The generator (critical):** `tools/gen_specialized.py` and
  `tools/astbuild.py` **emit** `AbstractMultiVector` into the generated modules
  (the generated classes subclass it and import it `from gacalc.base import
  AbstractMultiVector, ...`). So the rename must be made in the **generator**, not
  the generated output — then `make generate` re-emits `g1/g2/g3.py` + `scalar.py`
  with the new name. (Per the codegen rule: a correct change shows as a `tools/`
  diff with nothing under `src/gacalc/`.)
- **Generated (gitignored, regenerated):** `g1.py`, `g2.py`, `g3.py`, `scalar.py`.
- **Tests / notebooks:** `displaygraded.py`, `displayrotations.py`, and any test
  referencing the type.
- **`PKG-INFO`** (egg-info, regenerated on build — ignore).

## What to do

1. **`base.py`:** rename the class; update the `_OperandT` bound
   (`bound="MultiVectorBase"`) and every annotation/`isinstance`/`cast`.
2. **`gn.py` / `transforms.py` / `nbplotutils.py`:** rename imports + references.
3. **Generator:** replace the emitted string `"AbstractMultiVector"` everywhere in
   `tools/gen_specialized.py` (class bases, the `from gacalc.base import ...`
   header, `isinstance`/coerce helpers, `_OperandT` import) and `tools/astbuild.py`
   if it references the name. `make generate`; confirm the regenerated files use
   `MultiVectorBase` and `ty`/tests pass.
4. **Tests / notebooks:** update references.
5. Run `make test`, `make check-generated` (determinism), `ty check src tests`,
   `ruff`. Notebooks execute headless.

## Decision for Bill

- **Hard rename, or keep `AbstractMultiVector` as a deprecated alias?** The name
  appears in **notebooks** (user-facing teaching code) and is importable, so a
  hard rename is a (small) breaking change for anyone importing it. Options:
  (a) hard rename everywhere (cleanest; the repo is solo/pre-1.0); (b) rename +
  leave `AbstractMultiVector = MultiVectorBase` alias in `base.py` for
  compatibility. **Recommend (a)** unless you want the alias. Bill's call.

## Notes

- Mechanical but wide; safest as a single sweep (`grep -rl` + careful replace),
  then regenerate + full green suite. Watch the quoted string forms in the
  generator vs the live class references in source.
- Unrelated aliases stay: `MultiVector = Gn`, `MultiVectorFn`.
