# Prove the composition of two 2D rotations commutes (Lean + prose), and cite it in the rotate-from-a-to-b collapse

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

The "rotate from a to b" proof (`book/docs/proof-rotate-from-a-to-b.rst`, "The collapse" section) leans
on the fact that **the composition of two 2D rotations commutes** — doing one rotation then another
gives the same map in either order (`R₁ ∘ R₂ = R₂ ∘ R₁`) — but currently just *asserts* it ("In 2D,
rotations commute — turning by one angle and then another is the same in either order") with no proof or
reference. Give it
a proper backing in all three forms: **(1)** a named Lean theorem, **(2)** a **Python symbolic (sympy)
unit test**, **(3)** a short prose proof in the rotation chapter, and **(4)** make the collapse section
cite them explicitly instead of asserting. **Not started — this is the spec.**

## Why it's easy (the math)

2D rotations commute because **they add their angles** and addition is commutative: rotating by `θ`
then by `φ` is rotating by `θ+φ`, and `θ+φ = φ+θ`, so the order doesn't matter. In Lean this is a
one-liner from what already exists; in prose it's a one-paragraph corollary of angle addition.

## What to do

1. **Lean** — add the explicit named theorem(s) (verify `make lean` → `[lean] OK`, `sorry`-free):
   - In `proofs/GacalcProofs/Rotation2D.lean`: a `rot_comm` — `rot θ (rot φ v) = rot φ (rot θ v)` —
     proved from the existing `rot_add` (`rot θ (rot φ v) = rot (φ+θ) v`) plus `add_comm`. ~2 lines.
   - In `proofs/GacalcProofs/RotateFromTo2D.lean`: a `rotPlane_comm` — `rotPlane c₁ s₁ (rotPlane c₂ s₂
     v) = rotPlane c₂ s₂ (rotPlane c₁ s₁ v)` — a direct corollary of the existing `rotPlane_comp`
     (whose `(c₁c₂−s₁s₂, s₁c₂+c₁s₂)` result is already symmetric in the two pairs; the docstring even
     notes "rotPlane rotations commute"). This is the one the collapse actually uses (the sandwich is
     built from `rotPlane`), so name it so the page can cite it.
   - Optionally note in `rotPlane_conj_collapse`'s docstring that the collapse rests on `rotPlane_comm`.
2. **Python symbolic unit test** — a sympy-symbolic test that composing two 2D rotations commutes.
   Build two 𝒢₂ rotations with **symbolic angles** `θ`, `φ` (`sympy.symbols`) via the rotation API —
   `transforms.plane_rotation(Vector.e_1, Vector.e_2)` gives the factory, `plane_rotation(e_1,e_2)(θ)`
   the rotation — apply both orders to a symbolic vector (`compose([rot_θ, rot_φ])(v)` vs
   `compose([rot_φ, rot_θ])(v)`), and assert they are **symbolically equal** (`MultiVectorBase.
   symbolically_equal`, or `sympy.simplify` of each coefficient difference → 0; the trig may need
   `cos²+sin²=1` via the `subs=` hook). New `tests/test_rotation_commute.py` (or add to the existing
   rotation test file); runs under `make test` (`--doctest-modules`/pytest). LGPL-2.1 header, typed,
   ruff/ty clean.
3. **Prose** — add a short "rotations add, and so commute" result. Recommended home:
   `book/docs/proof-rotate.rst` (the rotation chapter, which ends on the angle/blend result) — state
   that composing two rotations adds their angles, hence rotating by `θ` then `φ` equals `φ` then `θ`.
   Keep it to a short paragraph (+ maybe one `.. math::` line); cite the Lean (`rot_comm`). Use the
   book's conventions (θ for the angle; symbols match any diagram).
4. **Reference it in the collapse** — in `book/docs/proof-rotate-from-a-to-b.rst` "The collapse",
   replace the bare assertion with an explicit pointer: link the rotation-chapter result ("2D rotations
   commute — :doc:`proof-rotate`") and cite the Lean theorem it rests on
   (`rotPlane_comm` in `proofs/GacalcProofs/RotateFromTo2D.lean`), so the step-3/step-1 cancellation is
   visibly justified rather than asserted.

## Gates

`make lean` green (new theorems, `sorry`-free); `make test` green (the new symbolic test passes);
`make docs` green (both pages render, the cross-reference resolves); `make format` green. Stage by path.

## Related

- `proofs/GacalcProofs/Rotation2D.lean` (`rot`, `rot_add`) and `RotateFromTo2D.lean` (`rotPlane_comp`,
  `rotPlane_conj_collapse`) — what the Lean builds on.
- `book/docs/proof-rotate.rst` (prose home) and `book/docs/proof-rotate-from-a-to-b.rst` "The collapse"
  (the citation site).
- `tasks/reference/lean-ga-proof-architecture.md` / `reduction-to-standard-position.md` — harvest the
  new theorem names on completion.
