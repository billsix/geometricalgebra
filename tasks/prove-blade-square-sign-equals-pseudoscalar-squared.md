# Prove the closed form == the pseudoscalar squaring, then optimize the helper to it

**Status:** proposed — needs go-ahead. **Phase 1 (`tasks/archive/2026/08/15/name-blade-square-sign.md`)
is DONE** — the named helper computes the sign the slow, obviously-correct way (actually squaring the
unit pseudoscalar). This task is the **optimization**: prove the closed form `(-1)^(r(r-1)/2)` is
equivalent, then substitute it back in. Created 2026-08-15 (William Emerison Six <billsix@gmail.com>).
**Priority:** 6
**Difficulty:** 3

## Direction (corrected 2026-08-15)

Phase 1 put the **obviously-correct** implementation in first: `pseudoscalar_squared_sign(r)` in
`base.py` returns `int(Gn.unit_pseudoscalar_squared(r).scalar_part())` — it *actually squares* the
`r`-dimensional unit pseudoscalar (in `Gn`, via a deferred import, since only a full algebra can
build it). This task proves the closed form equals that and swaps the closed form in as the
**optimized** version — the "make it correct, then make it fast" order.

## Goal — prove, then optimize (and it's fully reversible)

1. **Prove the equivalence.** For the `r`-dimensional unit pseudoscalar `I_r = e_1 e_2 … e_r`,
   `I_r² = (−1)^(r(r−1)/2)` (Euclidean): reversing `I_r` costs `r(r−1)/2` adjacent transpositions,
   each `e_i e_j → −e_j e_i`, and each `e_i² = +1`. Land it as a **test** asserting, over `r = 0..N`,
   `Gn.unit_pseudoscalar_squared(r).scalar_part() == (−1)^(r(r−1)/2)` — the durable proof. (Phase 1
   already spot-checked r=0..6; this makes it a permanent gate.)
2. **Substitute the optimized form.** Reimplement the helper body back to
   `return (-1) ** ((r * (r - 1)) // 2)` and **remove the deferred `from gacalc.gn import Gn`** — so
   the runtime callers (`Gn.reverse()`, `exp()`) go from squaring-a-pseudoscalar to O(1), and the
   `base → gn` coupling (introduced only for Phase 1's correctness) disappears. The call sites and
   the helper's *name/signature* do not change — only its body.
3. **Verify byte-identical behavior** (the `reverse`/`exp` suites are the guard; `pseudoscalar_squared_sign`
   returns the same `±1` for every `r`) + determinism + container gate.

## Scope — what actually gets faster (the maintainer's gen-time-constant point)

The sign is used at 4 sites, but they don't all pay at runtime:

- **Generated `reverse()` (both emitters in `tools/gen_specialized.py`)** — the generator evaluates
  the helper at **code-gen time** and bakes a `±1` **constant** into the emitted code. So the
  generated classes cost **nothing** at runtime *regardless* of the helper's body; this substitution
  doesn't change their generated output at all (same constant, just computed by formula instead of by
  squaring at gen-time).
- **`Gn.reverse()` and `exp()`** (non-generated, runtime) — these are the *only* callers that
  actually run the helper per call. They are where Phase 1's squaring is slow and where this
  optimization pays off.

## Undo / reversibility

This is a clean two-way swap of one function body (Phase 1 ↔ Phase 2): slow squaring ↔ closed form.
Either direction is a one-function edit plus a re-run of the gates; nothing else moves. Git history
(the Phase-1 commit and this one) records both forms.

## Open questions (for Bill)

1. **How far to optimize.** Substitute the closed form **everywhere** (simplest, and the proof makes
   it safe), or keep the pseudoscalar squaring somewhere as a living cross-check? Recommendation:
   substitute everywhere; the permanent equivalence test from step 1 *is* the cross-check.
2. Should the proof also live as a written note in `tasks/reference/` (a short "why the reversion
   sign is the pseudoscalar square"), or is the test enough? Recommendation: a 3-line reference note
   plus the test.
