# Extract r, I, θ (and a, b, conjugate) from a versor (Macdonald p85–86)

**Status:** blocked
**Priority:** 6
**Difficulty:** 5
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>) **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open questions below (runtime methods vs notebook formulas; the
scaled/un-normalized versor case; what "a and b" means; Macdonald edition/page).
**Recheck:** the Open questions below are answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"For vectors u,v, calculate r, I and theta, Macdonald page 85, and a and
b, and provide way to get complex conjugate, also on same page. As I think about this more from page 85,
I believe the u times v creates the rotor, so it's from that rotor that we can extract r, I, and theta.
I think this can work for gn, as well as be generated on all the rotor implementation. As I think about
it more, I think I do want to be able to extract a, B and I. Because from the rotor itself, I may be
scaled by some magnitude. To calculate R, look at page 86."*

From a versor formed by `u*v`, extract its magnitude `r`, unit bivector/plane `I`, and angle `θ` (and
`a`, `b`, and a complex-conjugate helper). Should work for `gn` and be generated on all versor
implementations.

## Context (investigation 2026-08-27)

- `Versor.plane_of_rotation()` already exists and yields the plane bivector `I` (generated
  `Versor.plane_of_rotation` (from `tools/gen_specialized.py`), in `g2`/`g3`) — but there is **no**
  `angle()`/`theta()` or scalar-magnitude `r` extractor, and **no** complex-conjugate helper
  (re-checked 2026-10-04).
- **Naming (gacalc 0.1.0, 2026-09-28):** the library renamed rotor → versor
  (`tasks/archive/2026/10/04/rename-rotor-to-versor.md`): `u*v` builds an **un-normalized** even versor
  (`versor_from_vectors`), so Q2's scaled case `R R̃ ≠ 1` is the *default* object, not an edge case;
  "rotor" in the quote above and below means the unit special case.
- **Lean evidence already in hand:** `proofs/GacalcProofs/Rotation2D.lean` machine-checks "the product
  of two unit vectors is the rotor of the angle between them" (`uvec_mul_uvec`:
  `(uvec α)(uvec β) = rotor (β − α)`, and `rotorFromTo_carry`) — i.e. θ extraction in 2D;
  `MathlibBridge.lean` identifies the 2D versor sandwich with Mathlib's `Orientation.rotation θ`.
- Reference doc `tasks/reference/unit-bivector-and-rotors.md` §3 "Rotor = exp(bivector)" and §5
  "Citations" have the versor math (`R = e^{−iθ/2}`, the Macdonald survey Eq. 2.3/2.4 citations, and
  the hyperbolic `γ₀v̂` scaled case from Macdonald's survey §4.1 — relevant to your "I may be scaled
  by some magnitude" and the "look at p86 for R" note).
- **Design tension to reconcile first:** `tasks/reference/book-outline.md` item 25 records a deliberate
  stance — *"we show theta but don't really need to calculate it — it's a property, not something to
  solve for."* This bullet wants to *compute* θ, so settle that first.
- Adjacent prior work (archived): `2026/06/06/document-rotor-methods.md`,
  `2026/08/15/redo-exp-book-referenced.md`, `2026/07/29/exp-for-rotors.md`. Adjacent active:
  `finalize-exp-citation.md` (cites Macdonald Eq. 2.3/2.4), `lean-rotor-3d-angle-theorem.md` (the 3D
  half-angle rotor rotates by its angle — the θ statement in 3D).

## Plan (draft — after questions)

- [ ] Reconcile with the book-outline "θ is a property, not solved-for" stance.
- [ ] Add extractors (`r`, `theta`/`angle`, `I` via existing `plane_of_rotation`, `conjugate`) — as
      runtime methods or notebook formulas per Q1 — handling the scaled/un-normalized versor (Q2).
- [ ] Symbolic checks; generate on all versor implementations (`gn`).

## Open questions

1. **Runtime methods or notebook formulas?** Should extraction produce methods (`r`, `theta`, `I`,
   `conjugate`) on `Versor`, or only notebook-demonstrated formulas?
2. **Scaled versor** — "should work for gn and all versor implementations": include the un-normalized case
   (`R R̃ ≠ 1`) where `r` is the sandwich scale factor?
3. **What is "a and b"** — recovering the two generating vectors `u, v` (not unique), or the even-part
   scalar/bivector components of the versor?
4. **Citation** — which edition/page of Macdonald? The reference doc cites the *Survey*; you say p85/p86.
