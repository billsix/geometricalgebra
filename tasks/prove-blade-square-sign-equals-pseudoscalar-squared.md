# Prove `(-1)^(r(r-1)/2)` == unit-pseudoscalar-squared sign, then substitute it out

**Status:** proposed — **gated on** [[name-blade-square-sign]] (Phase 1) landing first. Created
2026-08-15 (William Emerison Six <billsix@gmail.com>).
**Priority:** 6
**Difficulty:** 3

## Goal

Bill's conjecture: the sign `(-1)^(r(r-1)/2)` used in `reverse()`/`exp()` (see the Phase-1 task
[[name-blade-square-sign]]) **equals the sign of the `r`-dimensional unit pseudoscalar squared**.
This task (the "later task") is to (1) **prove** that, then (2) **substitute** the closed-form
exponent for a computation off the real pseudoscalar, so the code stands on the algebra rather
than a magic formula.

## Why this is tractable — the method already exists

`MultiVectorBase.unit_pseudoscalar_squared(cls, n)` is **already implemented**
(`src/gacalc/base.py:184`): it returns `unit_pseudoscalar(n) * unit_pseudoscalar(n)` — the actual
±1 (as a multivector). So the substitution target already exists; this task connects the Phase-1
name to it.

The identity to prove: for the `r`-dimensional unit pseudoscalar `I_r = e_1 e_2 … e_r`,
`I_r² = (−1)^(r(r−1)/2)` (Euclidean). Equivalently, a grade-`r` blade squares with that same sign
(`A² = (−1)^(r(r−1)/2)|A|²`) — which is exactly what `reverse()`/`exp()` rely on.

**Substitution scope (from the Phase-1 scan):** the sign is computed by formula at **4 sites** —
`base.py` `reverse()` + `exp()` (runtime) and `tools/gen_specialized.py:2146,2501` (the generator's
`reverse` emitters) — while `unit_pseudoscalar_squared` has **no internal caller** today. Once
Phase 1 routes all 4 through the named helper(s), this task swaps that single implementation to
compute off `unit_pseudoscalar_squared`, and every site benefits at once.

## Plan

1. **Prove the equivalence.** A short derivation (I_r reversal moves `r(r−1)/2` transpositions,
   each e_i e_j → −e_j e_i; each e_i²=+1) plus a **test** asserting, over `r = 0..N`,
   `unit_pseudoscalar_squared(r) == (−1)^(r(r−1)/2)` (as a scalar). The test is the durable proof.
2. **Substitute.** Reimplement the Phase-1 helper(s) so `pseudoscalar_squared_is_positive(r)`
   (and any signed-value sibling) computes from `unit_pseudoscalar_squared` rather than the
   exponent, and remove the `(-1) ** ((r * (r - 1)) // 2)` formula from `reverse()`/`exp()`.
3. Verify byte-identical behavior (the `reverse`/`exp` suites are the guard) + container gate.

## Open questions (for Bill)

1. **Performance/clarity tradeoff.** The exponent is O(1); `unit_pseudoscalar_squared(r)` builds
   and multiplies an actual pseudoscalar (more work, and `reverse()` runs per grade in a hot
   path). Options: substitute everywhere (clarity), keep the fast formula in `reverse()` but
   substitute in the (rare) `exp` guard, or memoize `unit_pseudoscalar_squared(r)` by `r`. Which
   do you want? Recommendation: substitute in `exp` (cold path) for sure; for `reverse` (hot),
   memoize or keep the formula — decide once the numbers are in.
2. Should the proof live as a test only, or also as a written note in
   `tasks/reference/` (a short "why the reversion sign is the pseudoscalar square")?
