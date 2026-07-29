# Extract the generated `_coerce` helper to `base.py`

**Status:** proposed — needs go-ahead to implement (investigated 2026-07-29)

## Facts (verified)

- `_coerce(x, cls)` is emitted as **raw text** from the generator's module-header
  template (`tools/gen_specialized.py`, the string block near the bottom that
  also carries the copyright/imports) into `g1.py`, `g2.py`, `g3.py` — three
  **byte-identical** copies.
- It is fully generic (parameterized by `cls`; zero per-algebra content) and is
  called only from the generated dispatch methods' `case _:` widen-fallback
  arms. Nothing hand-written calls it.
- No doc-region marker wraps it; mvp's book never `literalinclude`s it — no
  anchors break on moving it.
- It needs only `MultiVectorBase`, `Coef`, `sympy` — all already in `base.py`,
  so the move keeps the dependency graph acyclic. Precedent: `_OperandT`
  already lives in `base.py` and reaches the generated modules through the
  same import line.

## The change

1. Move the function verbatim to `base.py` (keep the `_coerce` name; it's an
   internal helper of the generated dispatch).
2. In the generator's header template, delete the function and add `_coerce`
   to the `from gacalc.base import MultiVectorBase, BladeCoef, Coef{operand_import}`
   line (the mechanism that already conditionally imports `_OperandT`).
3. `make generate`, then the gates: `make test`, `make check-generated`,
   `make check-regions`, `make format`.

## Trade-off (named, accepted)

The generated modules become one function less self-contained — a student
reading `g2.py` from site-packages sees an import instead of the definition.
Self-containment is already not absolute (the modules import
`MultiVectorBase`/`Gn`), and the house extraction rule applies directly:
three identical copies, more than one caller → one shared home.
