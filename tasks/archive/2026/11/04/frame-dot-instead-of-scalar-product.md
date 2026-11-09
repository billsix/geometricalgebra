# Use `dot` instead of `scalar_product` in `Frame`'s QR / peel code — done-record

**Completed:** 2026-11-04. Requested by William Emerison Six <billsix@gmail.com>: "it's not clear to me
why we use scalar product, when dot product is the same thing, and is likely more clear to the reader.
is it because scalar_product returns a real, so for typing reasons? if that's the case, I think it'd be
better to ensure the types are vectors as input, if it's not already checked, and use dot product, and
use typing cast if need be to real". Implemented by the agent.

## Why it was `scalar_product`

The return type, as the maintainer guessed. `MultiVectorBase.scalar_product(other) -> Real`, while
`dot` (the Hestenes inner product, an alias of `inner_product`) returns a multivector; on the generated
types `Vector.dot(Vector)` is typed to return the graded `Scalar` (the `scalar_spec` overload in
`tools/gen_specialized.py`). For two vectors the values agree, `a · b = ⟨a * b⟩ = a ∗ b`; for other
grades they differ (`tasks/reference/contraction-and-dot-definitions.md`).

## What was built

- **`a.dot(b).scalar_part()`** at the three call sites in `src/gacalc/frame.py`: `Frame.coefficients()`,
  the forward map of `to_invertible_function()`, and its `peel`. `MultiVectorBase.scalar_part() -> Real`
  (Hestenes & Sobczyk p. 4, `⟨A⟩₀`) reads the number out, so no `typing.cast` was needed. A bare cast
  would have been wrong: `dot`'s value really is a multivector. Three inline uses did not earn a helper.
  The same spelling replaced `scalar_product` in `tests/test_frame_class.py` and in the in-progress book
  notebooks `book/docs/notebooks/frame-qr-2d.py` / `frame-qr-3d.py` (`tasks/archive/2026/11/04/frame-notebooks-epix.md`).
- **Vector checks.** The frame's own vectors were already checked (`are_linearly_independent` raises on
  a non-vector). The map and its inverse were made to raise `ValueError` on a non-vector argument, through a
  nested `require_vector` shared by `forward` and `backward`. `test_map_rejects_a_non_vector` covers a
  bivector and a scalar in both directions. The `to_invertible_function()` docstring says so.
- **`CLAUDE.md`** › "Conventions the agent must obey while writing code" gained the rule: dot product for
  vectors (`a.dot(b).scalar_part()`, operands checked as vectors), `scalar_product` only where that
  operation is meant, as in Hestenes' own definitions (with the page cited).
- **`CHANGELOG.md`:** the `[Unreleased]` `Frame` entry was amended to say the map takes vectors only.

## Decisions

1. **`forward(x)` and `backward(y)` raise `ValueError` on a non-vector** (William Emerison Six
   <billsix@gmail.com>, 2026-11-04: "yes, raise ValueError on non-vector input"). A frame's map is only
   defined on vectors. The plan called for a changelogged breaking entry, but `Frame` is still under
   `[Unreleased] › Added` (never released), so no consumer can break. The existing entry was amended.
2. **The project-wide convention in `CLAUDE.md`** (William Emerison Six <billsix@gmail.com>, 2026-11-04):
   for vectors, a reader knows the dot product, not the scalar product.
3. **The other `scalar_product` calls in `src/` stayed.** Excluding the generated modules there are two,
   both in `base.py`: `magnitude_squared` (`self.reverse().scalar_product(self)`) and `cosine`
   (`(Ã ∗ B) / (|A| * |B|)`, H&S eq 1.53b). Both are Hestenes' general-multivector formulas, where the
   scalar product is the operation meant, so no follow-up task was needed.

## Verification (2026-11-04, the existing `gacalc` image)

- `pytest tests/test_frame_class.py src/gacalc/frame.py`: **26 passed** in 261 s (the 22 class tests, the
  new rejection test, and the `frame.py` doctests).
- `ruff check` and `ruff format --check` on `src` and `tests`: clean. `ty check src` and `ty check tests`:
  clean.
- `tools/check_annotations.py`: 43 findings in 14 files, none in `frame.py`, `test_frame_class.py` or the
  notebooks, so all are in files this change did not touch.
- The full `make test` / `make format` gate was run with the notebook work, on the rebuilt image
  (`tasks/archive/2026/11/04/frame-notebooks-epix.md`).
