# Fix broken notebook `rotate`; use `plane_rotation` instead

**Status:** complete
**Completed:** 2026-07-18
**Created:** 2026-07-18 (retroactive — documenting work already done)

> Retroactive record of a fix completed 2026-07-18. Verified in-container; the two
> notebook edits are in the working tree for Bill to commit.

## Problem (what Bill hit)

A notebook's inner `rotate(angle)` "didn't work because it was a function and
didn't have a latex expr." Root cause: the hand-rolled `rotate` constructed its
`InvertibleFunction` with **positional args in the wrong order**. The constructor
is `(func, latex_repr, inverse, latex_repr_inv)`, but the call passed
`(func, inverse_lambda, latex_str, latex_str)` — so:

- the **`latex_repr` field held a lambda**, and `_repr_latex_` does
  `"$" + self.latex_repr + "$"` → **`TypeError`** on display (the reported symptom);
- the **`inverse` field held a string**, so `inverse(rotate(θ))` was broken too.

The identical broken `rotate` existed in **both** `notebooks/displayg2.py` and
`notebooks/displaymv.py`.

## Fix

Replaced the hand-built `rotate` with the library's sanctioned planar-rotation
API, `plane_rotation(a, b)` (returns an `angle -> InvertibleFunction` factory whose
result renders its own LaTeX and does the half-angle rotor sandwich internally —
no hand-rolled rotor, per the CLAUDE.md rotation convention):

- **`notebooks/displaymv.py`** → `rotate = plane_rotation(e_1, e_2)`. Its `e_1`/`e_2`
  are the general **`Gn`** constants (from `gacalc.gn`); `plane_rotation` works with
  `Gn` directly. Added `plane_rotation` to the `from gacalc.gn import (...)` block.
- **`notebooks/displayg2.py`** → `rotate = plane_rotation(Vector2.e_1, Vector2.e_2)`.
  **Used the graded `Vector2` basis, NOT the module's `e_1`/`e_2`** (which are full
  `G2` and trip the library bug below). The rotor sandwich still preserves the
  notebook's `G2` values (`G2` in → `G2` out), so every existing call keeps working.
  Added `plane_rotation` to the `gacalc.transforms` import and **removed the
  now-unused `InvertibleFunction`** import. Updated the surrounding markdown cell to
  describe `plane_rotation` instead of the old `rotor_from_vectors` approach.

## Verification (in-container, real deps)

For both notebooks' actual usage patterns:
- `rotate(θ)._repr_latex_()` is a **string** (the old bug raised `TypeError` here);
- rotation is correct (`rotate(π/2)(e_1) == e_2`);
- **type preserved** — `G2` stays `G2`, `Gn` stays `Gn`;
- `compose([rotate(θ), translate(...)])` renders LaTeX; `inverse(...)` round-trips;
- numeric `rotate(0.0)` is the geometric identity (float-typed per the
  numeric-preservation convention; exact for a symbolic `0`).
- `ruff check` on both notebooks: **no new errors** (the 6 `E501` it reports are
  pre-existing prose lines in `displaymv.py`, unrelated); both `py_compile` clean.

## Follow-up discovered — real library bug (separate task)

`plane_rotation` **fails on full specialized `G1`/`G2`/`G3` operands** because the
**generated full-class `__add__` rejects a bare scalar** on both sides:
`(3*e_1) + 5` *and* `5 + (3*e_1)` both raise
`AttributeError: 'int' object has no attribute 'to_blade_dict'`. The base
`MultiVectorBase.__add__` handles scalars; the generated override
(`tools/gen_specialized.py`) drops that guard. `plane_rotation`'s rotor build does
`bivector*scalar + scalar`, so with a full-`G2` plane it hits this. `Gn` and the
graded `Vector`/`Bivector` types are fine.

This **contradicts CLAUDE.md's claim that `plane_rotation` "preserves
Gn/G1/G2/G3."** It is why `displayg2.py` had to use the `Vector2` basis rather than
the full-`G2` module constants. **Fix is in `tools/gen_specialized.py`** (add scalar
handling to the generated `__add__`, then regenerate + gate) — out of scope for the
notebook fix; see [[fix-generated-fullclass-add-scalar]] (proposed, if opened).
