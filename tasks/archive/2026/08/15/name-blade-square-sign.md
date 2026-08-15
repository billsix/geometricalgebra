# Name the blade-square sign, implemented the slow/obvious way (Phase 1)

**Status:** DONE 2026-08-15 (William Emerison Six <billsix@gmail.com>). **Corrected direction
(maintainer, 2026-08-15):** Phase 1 implements the sign the **slow, obviously-correct way** — it
*actually squares* the unit pseudoscalar — and the follow-up
`tasks/prove-blade-square-sign-equals-pseudoscalar-squared.md` proves the closed form
`(-1)^(r(r-1)/2)` is an equivalent optimization and substitutes it back in. (An earlier commit had
these reversed — fast formula first; `ac4ebfe` "…Im about to update it" was that checkpoint.)

Two module-level helpers in `base.py` — `pseudoscalar_squared_sign(r) -> int` (returns
`int(Gn.unit_pseudoscalar_squared(r).scalar_part())`, via a **deferred `from gacalc.gn import Gn`**
so the module graph stays acyclic — `Gn` is the only representation that can build the pseudoscalar;
a graded type silently returns 0) and `pseudoscalar_squared_is_positive(r) -> bool` (built on it) —
back the named uses at **all 4 sites**: `reverse()` and `exp()` (runtime) and both generator
`reverse` emitters (`tools/gen_specialized.py`).

**Cost is contained (the maintainer's gen-time-constant point):** the generator evaluates the helper
at **code-gen time** and bakes a `±1` **constant** into each generated `reverse()`, so the generated
classes pay **nothing** at runtime. Only the two non-generated runtime callers — `Gn.reverse()` (the
hand-written reference) and `exp()` (a base method) — do the squaring live. Generated output is
byte-identical to the fast version (same constants; determinism holds); 367 tests, ty clean, ruff
clean, doc-regions OK, container gate green. **Undoable:** the follow-up reverts the helper body to
`return (-1) ** ((r * (r - 1)) // 2)` and drops the `Gn` import.
**Priority:** 5
**Difficulty:** 2

## Goal

Give the bare magic expression `(-1) ** ((r * (r - 1)) // 2)` a **descriptive name** at its call
sites, so the code reads as what it *means* instead of an opaque exponent. **This phase only
names it — the implementation stays the same formula.** Proving the name is mathematically
justified, and swapping the formula for a computation off the real pseudoscalar, is the separate
follow-up [[prove-blade-square-sign-equals-pseudoscalar-squared]].

## What the expression is

For a grade-`r` blade `A` in Euclidean 𝒢ₙ, `A² = (−1)^(r(r−1)/2) · |A|²` — so
`(-1)**((r*(r-1))//2)` is the **sign of a grade-r blade's square** (equivalently: the reversion
sign for grade `r`, and — Bill's observation, to be proven in the follow-up — the sign of the
`r`-dimensional **unit pseudoscalar squared**). It is `+1` or `−1`.

## Call sites — the source scan (2026-08-15, Bill asked to scan for the pattern AND for `unit_pseudoscalar_squared` uses)

The `(-1)**((grade)*((grade)-1)//2)` sign appears **4 times**, all computing the same quantity
(the reversion sign / blade-square sign for a grade):

1. **`base.py:637` — `reverse()`** (runtime): the **signed value**,
   `((-1) ** ((r * (r - 1)) // 2)) * self.r_vector_part(r)` (reversion sign per grade `r`).
2. **`base.py:1056` — `exp()`** (runtime): the **predicate**,
   `if (-1) ** ((r * (r - 1)) // 2) != -1: raise ...` (reject positive-square; `!= -1` ≡ `== 1`).
3. **`tools/gen_specialized.py:2146`** (compile-time): `sign = (-1) ** ((len(b) * (len(b) - 1)) // 2)`
   per blade `b` — the generator emitting the full class's closed-form `reverse()`.
4. **`tools/gen_specialized.py:2501`** (compile-time): same, emitting the graded types' `reverse()`.

**`unit_pseudoscalar_squared` scan:** it is a real method (`base.py:184`, generated overrides in
g1/g2/g3, generator emitter at `gen_specialized.py:2234`) but has **no internal `src/` caller** —
only tests exercise it. So today the sign is recomputed by formula in all 4 sites above while the
"real" `unit_pseudoscalar_squared` sits unused internally. That is exactly the redundancy Phase 2
([[prove-blade-square-sign-equals-pseudoscalar-squared]]) collapses — and it confirms Bill's point
that naming this in ONE place makes every site benefit from the later optimization.

## Plan (Phase 1 — naming only; decisions locked)

- **`pseudoscalar_squared_sign(r) -> int`** — the signed value `(-1) ** ((r * (r - 1)) // 2)` (±1),
  used by `reverse()` (site 1) in place of the inline exponent.
- **`pseudoscalar_squared_is_positive(r) -> bool`** — `pseudoscalar_squared_sign(r) == 1` (build the
  predicate on the value helper, one formula), used by `exp()` (site 2) as
  `if pseudoscalar_squared_is_positive(r): raise ...`.
- **Runtime sites (1, 2):** both named — that's Bill's decision (scope = both), because the later
  substitution then benefits every caller at once.
- **Generator sites (3, 4):** same quantity but compile-time and using `len(b)`. **Decide whether to
  share** — the generator can import the helper from `gacalc.base` (it already puts `src/` on its
  path), so `sign = pseudoscalar_squared_sign(len(b))` unifies all 4; or leave the generator's local
  computation and just name the two runtime sites. Recommendation: unify (one definition of the
  sign), but flag if the import direction (build tool → library) is unwanted.
- **Keep the `(-1)**((r*(r-1))//2)` formula INSIDE the helper(s)** — do NOT route through
  `unit_pseudoscalar_squared` yet (that's Phase 2, gated on the proof).
- Location: module-level helpers in `base.py` (pure functions of an int grade). Phase 2 may promote
  them if computing off the real pseudoscalar wants an algebra/dimension context.
- Verify: `make test` + `ty` + `ruff` (host + container gate). Pure refactor → behavior
  byte-identical; the `reverse`/`exp` suites + the determinism gate (generator output unchanged) are
  the guards.

## Open questions (for Bill)

1. ~~Name~~ — **decided: `pseudoscalar_squared_is_positive` + `pseudoscalar_squared_sign`.**
2. ~~Scope~~ — **decided: both runtime sites.** Remaining sub-question: **also unify the 2
   generator sites** (import the helper into `tools/gen_specialized.py`), or leave them local?
   Recommendation: unify.
3. **Location:** module-level functions in `base.py` (proposed), or `@staticmethod` on
   `MultiVectorBase`? (Leaning module-level.)
