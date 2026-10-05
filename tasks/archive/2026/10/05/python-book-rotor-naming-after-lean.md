# Python + book: check the rotor/versor names against the Lean vocabulary

**Status:** done 2026-10-05 (`make test` 672 passed, format gate green); archived 2026-10-05
**Priority:** 7 **Difficulty:** 2
**Created / completed:** 2026-10-05 (William Emerison Six <billsix@gmail.com>) — the follow-on filed by Decision 5 of
`lean-unit-versors-rotors-sandwich-with-reverse.md` (this directory).
**Harvested to:** `tasks/reference/unit-bivector-and-rotors.md` §6 (vocabulary) and §8 (the 2D pedagogy in the book).

## BLUF

With Lean on the vocabulary *versor = even, any magnitude; rotor = unit versor, the sandwich object;
`fullAngleRotor` = the 2D one-sided full-angle teaching operator*, audited the Python package and the book for the
same words on the same objects. **No public Python name changed** (the package already matched), so there was no
`CHANGELOG` entry and no version bump; the book, a dozen test names, and several docstrings were brought into line.

## Context

- The maintainer's ordering: Python naming is checked **after** the Lean work landed. A pre-check during the Lean
  task had already found the package consistent: class `Versor`; `versor_from_vectors` / `versor_rotation` use the
  un-normalized `R v R⁻¹`; the half-angle unit object is built by `_unit_bivector_rotor_factory`'s `rotor_for`.
- `g2.py`/`g3.py` are generated; their docstrings live in `tools/gen_specialized.py`. The book's `.ipynb` are build
  artifacts regenerated from the `.py` by `entrypoint/docs.sh`, so only the `.py` is edited.

## Audit and what changed

| object | Lean | Python / book before | outcome |
|---|---|---|---|
| even element, any magnitude | `IsEvenVersor` | class `Versor` | match |
| un-normalized `b·a + \|a\|\|b\|` from two vectors | `versorFromVectors` | `versor_from_vectors` | match |
| inverse sandwich `R v R⁻¹` rotation | `sandwich` | `versor_rotation`, `MultiVectorBase.sandwich` | match |
| half-angle unit sandwich object | `rotor θ` | `_unit_bivector_rotor_factory` / `rotor_for` | match |
| one-sided full-angle 2D operator | `fullAngleRotor θ` | book: "the **rotor** `R = cos θ + sin θ e₁₂`" (geometric-product.rst/.py, blade-square-sign.rst) | **fixed**: "full-angle rotor", with the one-sided/2D-only reason and a pointer to the half-angle sandwich `plane_rotation` uses; notebook variable `rotor_result` → `full_angle_result` |
| tests on `versor_from_vectors` / `versor_rotation` named `test_rotor_*` | — | `test_graded` ×4, `test_transforms` ×3 (+ `rotor_fn`), `test_numeric_magnitude`, `test_plane_rotation`, `test_generator` | **fixed**: renamed to `versor` (`test_rotor_is_complex_2d`/`_quaternion_3d` → `test_versors_are_complex_numbers_2d`/`_quaternions_3d`); this also made `symbolic-equality.md`'s citation `test_versor_sandwich_equals_rotate_*` resolve (it had dangled) |
| docstrings calling the from-vectors versor a "rotor" | — | `base.py` (`versor_from_vectors` "builds the *rotor*"), `transforms.py` ×3 | **fixed** → versor |
| "unit rotor" / "rotation rotor" | — | generator → `g2.py`/`g3.py` `reverse`/`magnitude_squared` docstrings | **fixed** → "a rotor (a unit versor)" |
| `test_unit_bivector_i.py` cited `tasks/reference/unit-bivector-and-versors.md` | — | the file is `…-and-rotors.md` | **fixed** pointer |
| exp of a bivector "is a rotor" | `isRotor_expBivector*` | rotor | match (unit by construction) |

Gates, nested against the existing image: the `make test` command (672 passed) and the `make format` command
(ruff + ty clean). `make docs` was not run (prose-only `.rst`/notebook-markdown edits, no new roles or links); the
next docs build is the check. Committed by the maintainer in `6ab8028`.

## Related

- `lean-unit-versors-rotors-sandwich-with-reverse.md` (this directory)
- `tasks/reference/unit-bivector-and-rotors.md`
