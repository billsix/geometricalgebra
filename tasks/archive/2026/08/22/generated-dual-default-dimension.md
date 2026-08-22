# Generated `dual` — default `n` to the algebra dimension (the pseudoscalar grade), not `None`

**Status:** DONE 2026-08-22 (implemented + verified; interpretation confirmed by the maintainer)
**Priority:** 6
**Difficulty:** 2
**Created:** 2026-08-22

## Context

From a note (William Emerison Six <billsix@gmail.com>, 2026-08-22): *"for the generated dual,
should default to the grade, not zero."*

`MultiVectorBase.dual(self, n: int)` (in `base.py`) is the dimension-agnostic reference:
`A* = A · unit_pseudoscalar(n)⁻¹`, mapping a grade-r part to grade n−r. It **requires** `n` — a
`Gn` value has no intrinsic space dimension, so the caller must supply it (`Gn.dual()` raises
`TypeError: missing 1 required positional argument: 'n'`; `Gn.dual(3)` works).

The **generated** fixed-dimension types (`tools/gen_specialized.py` → `dual_method`, ~line 2485,
with `dim_mismatch_guard` ~line 1141) emit, for `G3`'s types:

```python
def dual(self, n: int | None = None) -> Vector:      # on Bivector
    if n is not None and n != 3:
        raise ValueError("Bivector.dual is fixed at dimension 3")
    return Vector(coeff_e_1=self.coeff_e_23, coeff_e_2=-self.coeff_e_13, coeff_e_3=self.coeff_e_12)
```

So the default argument is `None`, and the guard treats `None` as "use my own dimension". The
closed-form coefficients are baked at generation time, so `.dual()` with no argument **already**
produces the correct grade-(n−r) result (verified: `Bivector.e_12.dual()` → `Vector(…e_3=1)`,
`Scalar.one.dual()` → `Trivector(-1)`, `Trivector.e_123.dual()` → `Scalar(1)`). The `n` parameter is
retained only for Liskov compatibility with the base's `n`-required signature.

## What "default to the grade, not zero" likely means (to confirm)

The generated `dual` is already correct behaviourally, so the request reads as a **signature /
clarity** change rather than a bug fix. Best interpretation: the default value of `n` should be the
class's own dimension (the grade of that algebra's pseudoscalar — 3 for `G3`) so the signature is
self-documenting, instead of the opaque `None`:

```python
def dual(self, n: int = 3) -> Vector:                # default is the dimension, not None
    if n != 3:
        raise ValueError("Bivector.dual is fixed at dimension 3")
    ...
```

"not zero" is read as "not the empty/absent default" (`None`), i.e. give it the real dimension.

### Verified (2026-08-22, after `make generate`)

Every generated `dual` in `g3.py` already defaults to dimension 3 and is numerically correct — no
zero/degenerate result anywhere:

| type      | `.dual()` (no arg) | `.dual() == .dual(3)` |
|-----------|--------------------|-----------------------|
| `Scalar`  | `Trivector(-1)`    | ✓ |
| `Vector`  | `Bivector(…e_23=-1)` (for `e_1`) | ✓ |
| `Bivector`| `Vector(…e_3=1)` (for `e_12`) | ✓ |
| `Trivector`| `Scalar(1)`       | ✓ |
| `G` (full)| correct grade-reversed multivector | ✓ |
| `Rotor`   | `-> G` (odd part)  | ✓ |

`.dual(2)` on a `G3` type raises `ValueError("… is fixed at dimension 3")`. So the request is a
**signature/clarity** change (default `None` → dimension literal), not a behaviour fix — confirming
the open question below matters before any edit.

## Plan (pending confirmation of intent)

- [ ] Confirm the interpretation with the maintainer (see Open questions) before editing.
- [ ] In `tools/gen_specialized.py`, change `dual_method` to emit `n: int = <dim>` (the algebra
      dimension literal) instead of `n: int | None = None`, and simplify `dim_mismatch_guard`
      accordingly (`if n != <dim>:` — no `is not None` clause).
- [ ] Decide whether `Gn.dual` in `base.py` should gain a default too. It **cannot** default to a
      fixed dimension (dimension-agnostic), so likely leave it required — but note the asymmetry.
- [ ] Regenerate (`make generate`), re-run the doctest/conformance suite, `make check-regions`
      (the `<Class> dual method` doc-region must stay balanced), `ruff` + `ty check src`.
- [ ] Update the CLAUDE.md / reference note about the `n` param being "optional for Liskov compat"
      if the default changes from `None` to the dimension.

## Resolution (2026-08-22)

Maintainer confirmed: *"why would an argument to it default to anything but the grade? g2 should
default to 2, g3 to 3, etc; none should never be the default, or zero."* So the interpretation was
the signature change, not a behaviour bug.

**Done in `tools/gen_specialized.py`:**
- All three `dual` emission sites (Scalar dual, graded-type dual, full-class `dual_method`) now emit
  `n: int = <DIMENSION>` (default is the algebra dimension) instead of `n: int | None = None`.
- `dim_mismatch_guard` simplified from `if n is not None and n != <dim>` to `if n != <dim>` — since
  `n` can no longer be `None`, and 0/any-other value is the error it guards.
- Updated the `dual_method` comment and the reference doc
  (`tasks/reference/code-generator-architecture.md`, the dimension-fixed-methods section) to split
  `dual` (dimension-fixed, defaults to dim, raises on mismatch) from `unit_pseudoscalar` /
  `unit_pseudoscalar_squared` / `bases` / `symbolic_multivector` (which keep `n: int | None = None`
  with a real `super()` cross-dimension fallback — deliberately left unchanged).

**Verified:** `make generate` → g1 defaults `n=1`, g2 `n=2`, g3 `n=3`; `.dual()` == `.dual(<dim>)`;
`.dual(0)` / `.dual(<other>)` raise `ValueError`. 370 tests pass, `ty check src tests tools` clean,
`ruff check`/`format --check` clean, `check_doc_regions` OK.

**`Gn.dual` (base) left requiring `n`** — it is dimension-agnostic (a `Gn` value carries no space
dimension), so it cannot default to a fixed dimension. This asymmetry is intended; the generated
fixed-dimension types are exactly the ones that *can* know their own dimension.
