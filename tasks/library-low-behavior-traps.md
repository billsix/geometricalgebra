# Library traps: graded classmethods now raise instead of returning zero; `Gn.to_blade_dict()` returns a copy

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §4.3

## What was found (reproduced in a REPL)

- **Graded classmethods returned a silent zero:** `g3.Vector.unit_pseudoscalar(3)` gave a zero
  `Versor`, and `g3.Vector.bases(3)` and `g3.Vector.symbolic_multivector(3, "a")` gave zeros. A graded
  type drops the blades it has no field for, and `g3.Vector.one()` is already zero, so every product
  built from it collapses.
- **`Gn.to_blade_dict()` returned its internal dict:** `d = gn.e_1.to_blade_dict(); d[(2,)] = 5`
  changed the shared constant `gn.e_1` to `e_1 + 5 * e_2`. The review filed this as a low LEAD; it is
  a real corruption bug.
- **`signed_content([1 * e_1, 2 * e_1])` on `Gn` raising was not a bug.** `Gn` takes n from the
  largest basis index used (1), so k = 2 ≠ n, and `signed_content`'s `Raises:` documents a
  `ValueError` for k ≠ n. The documented 0 applies to a dependent set with k = n. Dropped.

## What changed

- **`base.py`:** a private `MultiVectorBase._require_holds_blade(value, blade)` raises
  `ValueError("<Type> cannot hold the basis blade <label>; use the full class")` unless the blade came
  out as itself. `unit_pseudoscalar` and `bases` call it (`bases` now loops per blade), and
  `symbolic_multivector` inherits it through `bases`. The full classes and `Gn` are unaffected, and
  the graded types' generated closed-form `dual` never called these.
- **`gn.py`:** `Gn.to_blade_dict()` returns `dict(self.coefficient_of_blade)`. The copy is cheap next
  to `Gn`'s eager `sympy.simplify`.
- **Tests:** `tests/test_graded.py` gained a parametrized test of the four raising cases and a test
  that the full class still builds every blade; `tests/test_multivector.py` gained a copy test.
- **`CHANGELOG.md` `[Unreleased]`:** a Changed entry (the new `ValueError` is a behaviour change)
  and a Fixed entry (the copy).

## Verification

`make test`: 775 passed, 2 skipped. `make format` and `make check-generated` pass.
