# Validate (or canonicalize) blade-dict keys in `from_blade_dict`

**Completed:** 2026-07-29

Spun off from `tasks/archive/2026/07/29/blade-dict-tests-and-comments.md` (found while pinning the
interchange contract, 2026-07-29). The maintainer chose **(a) raise**. Gate-verified: `make test`
312 passed; `check-generated`, `check-regions`, `format` all green.

## What "canonical key" means (plain terms)

A blade dict names each basis blade by a tuple of basis-vector indices: `{(1, 2): 4}` means
`4·e₁e₂`. **The library requires the indices in each key sorted ascending with no repeats**:
`(1, 2)`, never `(2, 1)` or `(1, 1, 2)`. The algebra is happy with `e₂e₁` (it equals `−e₁e₂`), so a
user might reasonably expect `Gn.from_blade_dict({(2, 1): 5})` to mean `−5·e₁e₂`. It does not: no
representation performs that sign flip; every `from_blade_dict` trusts its keys to be canonical.

## The behavior before the fix (measured 2026-07-29)

Same illegal input, two different silent wrong answers, nothing raised:

- **`Gn`** stored the `(2, 1)` key raw, a corrupted value: not equal to `−5·e₁e₂` (equality compares
  per key, and `(2, 1)` never matches `(1, 2)`), and products/grade ops built on it were garbage.
- **`G2`/`G3`/graded classes** silently dropped the key (their `from_blade_dict` reads only the
  canonical keys via `d.get((1, 2), 0)`), so `G2.from_blade_dict({(2, 1): 5})` was zero.

The precondition had been documented (the `BladeCoef` block in `base.py`) but deliberately not
test-frozen, which left the failure silent for anyone hand-writing a dict.

## Decision: (a) raise, not (b) canonicalize

- **(a) Raise on non-canonical keys**: cheapest, turns both silent corruptions into an immediate,
  explainable error.
- **(b) Canonicalize** (sort, apply the permutation sign, annihilate repeated indices, merge):
  friendlier, but more machinery per representation, and it quietly blesses an input style the docs
  discourage (basis-vector construction is the taught path; `decrease_grade` in
  `Gn._geometric_product` already owns this logic for products).

(a) won because `from_blade_dict` is an interchange/constructor primitive, not user-facing sugar;
loud rejection fits its role, and (b) can be layered on later.

## What shipped

- One shared validator, `_require_canonical_blades(blade_coef)` in `base.py` (the same shared-home
  pattern as `_coerce`), called by every representation's `from_blade_dict`: `Gn`'s directly, the
  generated classes' via an emitted call (`tools/gen_specialized.py`, `from_blade_dict_method`), with
  the helper added to the generated modules' base import.
- A non-canonical key raises `ValueError` naming the offending key and explaining the fix (sorted
  key, sign folded into the coefficient; a repeated index contracts). Canonical-but-foreign keys
  still silently drop in graded types; that contract is unchanged.
- Docs: the `BladeCoef` block and the abstract `from_blade_dict` docstring in `base.py` state the
  raise (no more "undefined behavior").
- `tests/test_blade_dict.py` gained `test_non_canonical_keys_raise` (covering `(2, 1)` and `(1, 1)`)
  and an updated module docstring; the existing 9 contract tests stayed green. Suite: 312.
