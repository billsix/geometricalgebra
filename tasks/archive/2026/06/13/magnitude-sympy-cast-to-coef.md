# Why is multiplying magnitudes cast to a sympy expression instead of Coef?

**Status:** complete
**Completed:** 2026-06-13
**Created:** 2026-06-13

## Outcome

Resolved in two parts:
- **Functional** (via `[[magnitude-numeric-for-numeric-input]]`): `magnitude()`
  and `inverse()` now keep numeric `float` input numeric, so "multiplying
  magnitudes" (`abs(a)*abs(b)` in `rotor_from_vectors`, and `cosine()`) no longer
  produces sympy for numeric input; `int` stays exact (`Rational`), symbolic stays
  symbolic. The `base.py:502` `sympify` was replaced by that numeric/exact split.
- **Cosmetic** (here): the rotor scalar was built via `from_sympy_expr(scale)`,
  a misleadingly-named constructor that *looked* like a sympy cast but is just
  `from_blade_dict({(): s})`. Renamed **`from_sympy_expr` → `from_coef`** (def +
  callers in `base.py`, and the `_coerce` template in `tools/gen_specialized.py`);
  regenerated `g*.py`. Verified: full suite 225 passed; generator output
  byte-deterministic; no `from_sympy_expr` left anywhere.

## Goal

Figure out why something gets **cast to a sympy expression** when it's *just
multiplying magnitudes together*, rather than staying a plain `Coef`. The
suspicion: this was a workaround from when **casting to `Coef` didn't work**. Given
recent updates (the `Coef` type and magnitude path have changed), it may now be
possible to **just cast to `Coef`** — investigate, and simplify if so.

## Where to look

- `Coef = int | float | sympy.Expr` — `src/gacalc/base.py:37`.
- `magnitude()` returns `sympy.sqrt(self.magnitude_squared())` — `base.py:229`.
  `sympy.sqrt` **always** returns a `sympy.Expr`, even for int/float input — so
  `abs(a) * abs(b)` is `sympy.Expr × sympy.Expr` ⇒ a sympy expression. This is a
  prime candidate for the "cast to sympy when just multiplying magnitudes" Bill
  describes.
- `mag_sq = sympy.sympify(self.magnitude_squared())` — `base.py:502`, with the
  comment (lines ~499–502) that this is **deliberate**: for the specialized reps,
  the value "silently degrades to a float — sympify keeps it exact (Rational)."
  This is very likely the "why casting didn't work" history.
- `base.py:749` carries a comment "needed now that `magnitude()` is typed `Coef`
  (int | float | sympy.Expr)" — i.e. the type already changed once; check what that
  unblocked.

## Plan

- [ ] **Pin down the exact cast Bill means.** Trace where two magnitudes get
      multiplied (the rotor / `normalize` / reciprocal path — see
      `[[geometric-product-magnitude-proof]]`, which wants `abs(from*to)` instead of
      `abs(from)*abs(to)`) and identify the specific sympy cast in play
      (`magnitude()`'s `sqrt`, the `sympify` at `base.py:502`, or another).
- [ ] **Recover the history.** Confirm *why* the sympy cast was introduced —
      the `base.py:499–502` comment says it preserves exactness (Rational) where a
      specialized representation would degrade to float. Decide whether that reason
      still holds.
- [ ] **Test the "just cast to Coef" hypothesis.** Given current types, try keeping
      the value as `Coef` (or an explicit `Coef` cast) instead of forcing sympy;
      check it doesn't reintroduce the float-degradation / loss-of-exactness that
      motivated the original cast, across `scalar`/`g1`/`g2`/`g3`/`gn`.
- [ ] **Simplify if safe**, and verify: run the suite (regression + the
      `--doctest-modules` examples). Mind the codegen reps (edit source/template +
      regenerate, don't hand-edit `g2.py`/`g3.py`).

## Notes / decisions

- Overlaps with `[[geometric-product-magnitude-proof]]` — both touch how magnitudes
  combine in the rotor construction; sequence them together.
- The exactness concern (Rational vs float for specialized reps) is the thing most
  likely to bite — that's probably the original reason for the sympy cast, so the
  cleanup has to preserve it.
- Codegen + `--doctest-modules` constraints apply (see `CLAUDE.md`).

## Open questions

- Which exact cast is the target — `magnitude()`'s `sympy.sqrt`, the
  `sympy.sympify` at `base.py:502`, or the magnitude *product* in the rotor path?
- Does dropping the sympy cast risk float-degradation / loss of exactness for the
  specialized representations (the original rationale)?
- Do this before, after, or together with the magnitude proof task?
