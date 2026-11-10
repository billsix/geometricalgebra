# Every class has a usable `one()`; remove `frame._scalar_one`

**Status:** in progress — questions answered (see Decisions)
**Priority:** 3
**Difficulty:** 5
**Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>)
**Branch:** `sp-rotations-guards-enums-examples`

## BLUF

`frame._scalar_one(vector)` exists because a graded type's `one()` is wrong: `MultiVectorBase.one()`
is `cls.from_real(1)` returning `Self`, and a graded `Vector_n` has no scalar slot, so
`Vector.one()` silently drops to the zero vector (the "exp() trap"). The helper works around it with
`type(vector.dot(vector)).one()`. The maintainer wants each class to carry the notion of one, as it
carries zero, so the helper is not needed. Then investigate what else belongs on the class the same
way (candidates: the pseudoscalar `I`, `basis_vector`/basis constants, an identity
`InvertibleFunction`, the scalar type itself). Done means: `X.one()` is the scalar 1 for every class
(typed as the scalar type for graded classes), `_scalar_one` is gone and its three call sites in
`frame.py` use the class, the investigation's findings are recorded with a decision each, gate green,
CHANGELOG entry.

## Context (read first)

- `src/gacalc/base.py` `zero`/`one`/`from_real`; `src/gacalc/frame.py` `_scalar_one` and its callers
  (`prefix_blades` and the two wedge reductions).
- `tasks/reference/blade-dict-interchange.md` (graded silent-drop); generated classes:
  `tools/gen_specialized.py`, `tasks/reference/code-generator-architecture.md`,
  `generated-product-typing.md`.
- Typing: a graded `Vector.one()` returning `Scalar` changes its return type from `Self`; ties into
  `tasks/typing-base-return-types-redesign.md` (parked).

## Plan

1. Generator emits `one()` on each graded class returning that algebra's `Scalar` (and `Odd_3` etc.
   likewise); `Gn`/full `G` keep `Self`.
2. Replace `_scalar_one(v)` with `type(v).one()`; delete the helper; doctests.
3. Investigation of other class-level notions; implement only those decided.

## Decisions

- A graded class's `one()` returns **that algebra's `Scalar`** (its return type changes from `Self`) (William Emerison Six <billsix@gmail.com>, 2026-11-10).
