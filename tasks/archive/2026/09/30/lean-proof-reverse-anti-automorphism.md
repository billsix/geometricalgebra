# Lean proof: reverse is an anti-automorphism — reverse(A B) = reverse(B) reverse(A)

**Status:** DONE 2026-09-30 (committed `b6c5bc5`) — verified `sorry`-free by the Lean gate
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## Outcome (2026-09-30)

Landed and gate-verified (`proofs/check.sh`: `Build completed successfully`, no `sorry`/`admit`):
- **G2** (`proofs/GacalcProofs/G2.lean`): `reverse_mul` (anti-automorphism), `reverse_vec`,
  `reverse_of_isVector`, `reverse_mul_vec` (`(ab)~=ba`, 2D).
- **G3** (`proofs/GacalcProofs/Sandwich.lean`): `reverse_of_isVector`, `reverse_mul_vec`
  (`(ab)~=ba`), `reverse_mul3_vec` (`(abc)~=cba`, via `reverse_mul` ×2 + `mul_assoc`).
Covers `foo.txt` item 3 exactly. Inventory updated in `tasks/reference/lean-ga-proof-architecture.md`.
Open questions Q1/Q2 resolved as recommended (IsVector hypotheses; 2D+3D for `ab`, 3D for `abc`).

## BLUF

Prove in Lean that reversal reverses the order of a product — the anti-automorphism law
`reverse(A·B) = reverse(B)·reverse(A)` — and its named vector corollaries the maintainer asked
for: **`reverse(a·b) = b·a`** (2D) and **`reverse(a·b·c) = c·b·a`** (3D), for vectors. This is a
small, mostly-mechanical task: the general G3 law is **already proven**; what's missing is the
**G2** version and the **named vector corollaries** in both dimensions. "Done" = the theorems land
in the Lean tree, `make lean` stays green (`sorry`-free), and each is a from-scratch coordinate
proof consistent with the existing style.

## Context (read first)

- Lean tree: `proofs/GacalcProofs/*.lean`, gate `make lean` (`proofs/check.sh`, green 2026-09-30).
  Orientation `tasks/reference/lean-for-gacalc.md`; architecture `tasks/reference/lean-ga-proof-architecture.md`.
- The Python `reverse` this mirrors: `src/gacalc/base.py:1162`.

## Current state — what's already there to build on

- **PROVEN (general, G3):** `GacalcProofs.G3.reverse_mul` — `proofs/GacalcProofs/Sandwich.lean:354`
  — `reverse (mul a b) = mul (reverse b) (reverse a)`, proof `by simp only [reverse, mul]; ext <;> ring`.
  Docstring already calls it "Reverse is an anti-automorphism; general (no evenness needed)."
  Currently used only by `inverse_mul` (`Sandwich.lean:370`).
- **MISSING (G2):** there is no `G2.reverse_mul`. G2 has `reverse` (`G2.lean:81`) and
  `reverse_reverse` (involution, `G2.lean:84`) but not the product law. Add it in the G2 namespace
  in `Sandwich.lean` (lines 14-93) or `Versor2D.lean`; expect the same one-liner
  `by simp only [reverse, mul]; ext <;> ring` (G2 `reverse`/`mul` are `G2.lean:81/60`).
- **MISSING (the named vector corollaries):** neither `reverse(a·b)=b·a` nor `reverse(a·b·c)=c·b·a`
  exists as a named theorem in either dimension. They follow trivially:
  - `reverse(a·b) = reverse(b)·reverse(a) = b·a` because reverse fixes a vector — G3 already has
    `reverse_vec` (`G3.lean:257`); **G2 lacks a `reverse_vec`** (add it — reverse only flips `c12`,
    so it fixes a G2 vector trivially).
  - `reverse(a·b·c) = c·b·a` follows from `mul_assoc` (`AlgebraLaws.lean:67`) + `reverse_mul` +
    `reverse_vec`.

## Plan (on go-ahead)

1. Add `G2.reverse_mul` (+ `G2.reverse_vec` if not present) in the G2 namespace.
2. Add named vector corollaries in both dimensions: `reverse_mul_vec` (`reverse(a·b)=b·a`) and
   `reverse_mul3_vec` (`reverse(a·b·c)=c·b·a`), each stated for `IsVector` hypotheses (G3) /
   `vec`-constructed inputs, using the existing `reverse_vec` + `mul_assoc`.
3. `make lean` green; `#print axioms` clean (only `propext/Classical.choice/Quot.sound`).
4. If a proof-notebook exists (see `tasks/investigate-lean-to-python-proof-notebooks.md`), this is
   a good candidate to also show `show_mult`-style — cross-link, don't build it here.

## Overlap check

No existing task covers the reverse anti-automorphism (checked all 7 `lean-proof-*` /
`investigate-lean-*` tasks; `reverse_mul` was added incidentally to support `sandwich_comp`).
Safe to create. Distinct from `tasks/lean-general-multivector-inverse.md` (that's the mixed-grade
*inverse*, which merely *uses* `reverse_mul`).

## Open questions

1. **Corollary statement form:** state the vector corollaries with `IsVector a`/`IsVector b`
   hypotheses on the flat struct (the current G3 idiom, `G3.lean:214`), or over `vec`-constructed
   inputs `vec x y z`? My lean: `IsVector` hypotheses — more general and matches `reverse_vec`.
2. **Is the 3-vector chain wanted in 2D too**, or is `reverse(a·b·c)=c·b·a` a 3D-only ask? (The
   note says "in 3D"; 2D is trivially the same proof if wanted.)
