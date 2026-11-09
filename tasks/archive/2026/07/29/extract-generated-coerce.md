# Extract the generated `_coerce` helper to `base.py`

**Completed:** 2026-07-29

## Outcome

`_coerce` was moved verbatim to `base.py` (its docstring extended to say it is the shared
widen-fallback helper the generated modules import), and the generator's header template emits the
import instead of the definition. Gate-verified: `make test` 302 passed; `check-generated`,
`check-regions`, `format` all green. Stale descriptions in
`tasks/reference/code-generator-architecture.md` (header-emitted `_coerce`; "falls through to the
`case T()` arm") were corrected in the same change.

## Facts (verified)

- `_coerce(x, cls)` had been emitted as **raw text** from the generator's module-header template
  (`tools/gen_specialized.py`, the string block that also carries the copyright/imports) into
  `g1.py`, `g2.py`, `g3.py`: three byte-identical copies.
- It is fully generic (parameterized by `cls`; zero per-algebra content) and called only from the
  generated dispatch methods' `case _:` widen-fallback arms. Nothing hand-written calls it.
- No doc-region marker wrapped it, and mvp's book never `literalinclude`s it, so no anchors broke.
- It needs only `MultiVectorBase`, `Coef`, `sympy`, all already in `base.py`, so the move keeps the
  dependency graph acyclic. Precedent: `_OperandT` already lived in `base.py` and reached the
  generated modules through the same import line.

## The change

1. The function moved verbatim to `base.py`, keeping the `_coerce` name (an internal helper of the
   generated dispatch).
2. The header template dropped the function and added `_coerce` to the
   `from gacalc.base import MultiVectorBase, BladeCoef, Coef{operand_import}` line (the mechanism
   that already conditionally imports `_OperandT`).

## Trade-off (named, accepted)

The generated modules became one function less self-contained: a student reading `g2.py` from
site-packages sees an import instead of the definition. Self-containment was already not absolute
(the modules import `MultiVectorBase`/`Gn`), and the house extraction rule applies directly: three
identical copies, more than one caller → one shared home.
