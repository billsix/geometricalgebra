# Rename AbstractMultiVector -> MultiVectorBase

Status: **proposed — needs go-ahead** · 2026-06-11 (Bill)

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
