# Validate (or canonicalize) blade-dict keys in `from_blade_dict`

**Status:** proposed — needs a decision from Bill between options (a) and (b)
below. Spun off from `tasks/archive/2026/07/29/blade-dict-tests-and-comments.md`
(found while pinning the interchange contract, 2026-07-29).

## What "canonical key" means (plain terms, worked example)

A blade dict names each basis blade by a tuple of basis-vector indices:
`{(1, 2): 4}` means `4·e₁e₂`. **The library requires the indices in each key
to be sorted ascending with no repeats** — `(1, 2)`, never `(2, 1)` or
`(1, 1, 2)`. That sorted form is the "canonical key."

Why there's a wrong way to write it at all: the *algebra* is perfectly happy
with `e₂e₁` — it equals `−e₁e₂` (swapping adjacent basis vectors flips the
sign). So a user might reasonably think

```python
Gn.from_blade_dict({(2, 1): 5})     # "5·e₂e₁, i.e. −5·e₁e₂"?
```

means `−5·e₁e₂`. **It does not.** No representation performs that sign flip;
`from_blade_dict` on every class trusts the keys to already be canonical.

## What actually happens today (measured 2026-07-29) — the bug-shaped part

The two representations fail **differently**, and both silently:

- **`Gn`** stores the `(2, 1)` key **raw**, producing a corrupted value: it is
  NOT equal to `−5·e₁e₂` (equality compares dict entries per key, and `(2, 1)`
  never matches `(1, 2)`), and products/grade ops built on it are garbage.
- **`G2`/`G3`/graded classes** silently **drop** the key entirely (their
  `from_blade_dict` reads only the canonical keys via `d.get((1, 2), 0)`), so
  `G2.from_blade_dict({(2, 1): 5})` is simply zero.

Same illegal input, two different silent wrong answers. Nothing raises.

The precondition is now *documented* (the `BladeCoef` comment block in
`base.py`) and the divergent behaviors are deliberately **not** test-frozen
(they are accidents, not contract) — but documentation alone still leaves the
failure silent for anyone who hand-writes a dict.

## The two possible fixes — pick one

**(a) Raise on non-canonical keys** (recommended). In each
`from_blade_dict`, reject any key whose indices are not strictly increasing:
`ValueError("blade key (2, 1) is not canonical; write (1, 2) and flip the
coefficient sign")`. Cheapest, turns both silent corruptions into an
immediate, explainable error. For the generated classes this is a small
emission in `tools/gen_specialized.py`; for `Gn` a check in its
`from_blade_dict`/`__post_init__`. The abstract docstring in `base.py` states
the contract.

**(b) Canonicalize** — accept any key, sort the indices, apply the
permutation sign, annihilate repeated indices (`e₁e₁ = 1`), and merge into
the canonical entry. Friendlier (hand-written dicts "just work"), but more
machinery duplicated per representation, and it quietly blesses an input
style the rest of the docs discourage (basis-vector construction is the
taught path; `decrease_grade` in `Gn._geometric_product` already owns this
logic for products).

Recommendation: **(a)** — `from_blade_dict` is an interchange/constructor
primitive, not user-facing sugar; loud rejection fits its role, and (b) can
always be layered on later if wanted.

## Verification (once decided)

- Unit tests in `tests/test_blade_dict.py`: the currently-undefined inputs
  (`(2, 1)`, `(1, 1)`) get pinned to the chosen behavior for `Gn`, a full
  class, and a graded class; the existing 9 contract tests stay green.
- Update the `BladeCoef` comment block in `base.py` (it currently says
  "undefined behavior" — after this task it should state the chosen rule).
- Gates: `make test`, `make check-generated`, `make check-regions`,
  `make format`.
