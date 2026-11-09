# Name the blade-square sign, implemented the slow/obvious way (Phase 1)

**Created:** 2026-08-15 · **Completed:** 2026-08-15

Gave the bare expression `(-1) ** ((r * (r - 1)) // 2)` a **descriptive name** at its call sites,
so the code reads as what it means. For a grade-`r` blade `A` in Euclidean 𝒢ₙ,
`A² = (−1)^(r(r−1)/2) · |A|²`, so the expression is the **sign of a grade-r blade's square**
(equivalently the reversion sign for grade `r`, and, by the maintainer's observation, the sign of
the `r`-dimensional unit pseudoscalar squared). It is `+1` or `−1`.

**Direction (corrected by the maintainer, 2026-08-15):** Phase 1 implements the sign the **slow,
obviously correct way**, by actually squaring the unit pseudoscalar; the follow-up
`tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md` proved the closed
form `(-1)^(r(r-1)/2)` an equivalent optimization and substituted it back in. An earlier commit had
the order reversed (fast formula first); that checkpoint commit ("…Im about to update it") was later squashed away.

## The source scan (2026-08-15)

At the maintainer's request the source was scanned for the pattern and for
`unit_pseudoscalar_squared` uses. The sign appeared **4 times**, all the same quantity:

1. `base.py` `reverse()` (runtime): the signed value, `sign * self.r_vector_part(r)`.
2. `base.py` `exp()` (runtime): the predicate, `if sign != -1: raise ...` (reject a
   positive-square blade).
3. `tools/gen_specialized.py` (code-gen time): `sign` per blade `b` (`len(b)`), emitting the full
   class's closed-form `reverse()`.
4. `tools/gen_specialized.py` (code-gen time): the same, emitting the graded types' `reverse()`.

`unit_pseudoscalar_squared` was a real method (`base.py`, generated overrides in g1/g2/g3, a
generator emitter) with **no internal `src/` caller**; only tests used it. Naming the sign in one
place meant every site would benefit from the later optimization (the maintainer's point).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-15)

- **Names:** `pseudoscalar_squared_sign(r) -> int` (the ±1 value) and
  `pseudoscalar_squared_is_positive(r) -> bool`, built on the value helper (one formula).
- **Scope:** both runtime sites, and the two generator sites too: the generator imports the helper
  from `gacalc.base` (it already has `src/` on its path), so all 4 sites share one definition.
- **Location:** module-level functions in `base.py` (pure functions of an int grade), not a
  `@staticmethod` on `MultiVectorBase`.

## What changed

- `pseudoscalar_squared_sign(r)` returns `int(Gn.unit_pseudoscalar_squared(r).scalar_part())`, via
  a **deferred `from gacalc.gn import Gn`** so the module graph stays acyclic (`Gn` is the only
  representation that can build the pseudoscalar; a graded type silently returns 0).
- `reverse()` uses the value helper; `exp()` uses
  `if pseudoscalar_squared_is_positive(r): raise ...`; both generator `reverse` emitters use the
  value helper.
- **Cost stayed contained** (the maintainer's gen-time-constant point): the generator evaluates
  the helper at code-gen time and bakes a `±1` constant into each generated `reverse()`, so the
  generated classes pay nothing at runtime. Only `Gn.reverse()` (the hand-written reference) and
  `exp()` (a base method) square live.
- The change is undoable by reverting the helper body to `return (-1) ** ((r * (r - 1)) // 2)` and
  dropping the `Gn` import, which the follow-up did.

## Verification

Generated output was byte-identical to the fast version (same constants; determinism held); 367
tests, ty clean, ruff clean, doc-regions OK, container gate green.
