# Lift G2's coordinate-leaking theorem conclusions to G3's object-out form

**Status:** proposed — needs go-ahead (to be looked at after the current file-structure work). Scope
**decided** (maintainer, 2026-10-28): **audit all of G2 and lift every genuine case**, not just the
two named theorems — keep the deliberate equivalence bridges (e.g. `dot_eq_coord_sum`) coordinate.
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Some `G2.lean` theorems take geometric objects in (`{a b : G2} (ha : IsVector a) …`) but **conclude
with a raw coordinate expression**, where the `G3.lean` twin already concludes about the object. The
clearest case: `dot_is_sym_part` is commented "the dot product **is** the scalar part of ½(ab + ba)"
yet concludes `(…).s = a.c1 * b.c1 + a.c2 * b.c2` — a coordinate sum, not `dot a b`. This violates
the house rule *"geometric objects in, scalars in the body, geometric objects **out**"*
(`CLAUDE.md`, `tasks/reference/lean-ga-proof-architecture.md`). "Done" = each such G2 theorem is
lifted to the full object-equality form its G3 twin already uses, downstream consumers updated,
`make lean` green.

## Context (cold start)

- Raised 2026-10-28 by the maintainer while reviewing `G2.dot_is_sym_part`/`wedge_is_antisym_part`
  during the file-structure sweep (`tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`). Sibling of
  [[lean-basis-constants-self-documenting]]; both are "make the contents live up to the comment,"
  and both are **content** changes out of scope for the content-preserving reorder sweep.
- The defect is a **weaker interface**, not a wrong proof: the current G2 statements pin only the
  relevant component (`.s` / `.c12`) and equate it to a coordinate sum; the object form is strictly
  stronger (it also asserts the other components vanish) and is what the comment promises.

## The two known cases (G2 current vs. the G3 twin it should match)

`proofs/GacalcProofs/G2.lean`, current:
```lean
theorem dot_is_sym_part {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (smul (1 / 2) (add (mul a b) (mul b a))).s = a.c1 * b.c1 + a.c2 * b.c2 := by
  obtain ⟨has, ha12⟩ := ha; obtain ⟨hbs, hb12⟩ := hb
  simp only [smul, add, mul, has, ha12, hbs, hb12]; ring

theorem wedge_is_antisym_part {a b : G2} (ha : IsVector a) (hb : IsVector b) :
    (smul (1 / 2) (sub (mul a b) (mul b a))).c12 = a.c1 * b.c2 - a.c2 * b.c1 := by
  obtain ⟨has, ha12⟩ := ha; obtain ⟨hbs, hb12⟩ := hb
  simp only [smul, sub, mul, has, ha12, hbs, hb12]; ring
```

`proofs/GacalcProofs/G3.lean`, the target shape:
```lean
theorem dot_is_sym_part … : smul (1 / 2) (add (mul a b) (mul b a)) = smul (dot a b) one := by
  obtain …; simp only [smul, add, mul, dot, one, …]; ext <;> ring
theorem wedge_is_antisym_part … : smul (1 / 2) (sub (mul a b) (mul b a)) = wedge a b := by
  obtain …; simp only [smul, sub, mul, wedge, …]; ext <;> ring
```

So lift G2's conclusions to `= smul (dot a b) one` and `= wedge a b`, adding `dot`/`one`/`wedge` to
the `simp only` set and an `ext <;> ring` (the goal is now an object equality, like G3's proof).

## Method

1. **Audit, don't assume two.** Grep `G2.lean` for theorems that take `IsVector`/`IsScalar`/
   `IsBivector` and whose conclusion is a `.s`/`.c1`/`.c12 = <coordinate expression>` or a bare
   coordinate sum — list every one where the G3 twin (or the house style) says it should be an
   object equality. Candidates to check beyond the two above: `dot_eq_coord_sum` (this one is a
   deliberate "equivalence to the general case" coordinate bridge — likely keep), the `_vec`
   coordinate leaves (keep — their RHS *is* coordinate arithmetic, per the A/B/C "C-keep" rule).
2. **Lift each genuine case** to the G3-twin object form; adjust the proof (`ext <;> ring`).
3. **Update consumers.** A strengthening can break a caller that `rw`/`simp`-matched the exact old
   `.s = …` RHS. `rg` each lifted theorem's name across `proofs/GacalcProofs/`, fix call sites,
   `make lean` after each.
4. Reconcile `tasks/reference/lean-ga-proof-architecture.md` if its A/B/C examples cite the old form.

## Risk / verification

- Strengthening statements — the risk is downstream call sites, not the proofs themselves. `make lean`
  (USE_LEAN image, `proofs/check.sh`) is the gate; verify after each lifted theorem.
- Lean only; generated Python untouched. Own commit (a content change, not the reorder sweep).

## Deliverables

- Every coordinate-leaking G2 conclusion that has an object-out G3 twin lifted to match; consumers
  updated; `make lean` green; the A/B/C examples in the architecture doc still accurate.

See also: [[lean-basis-constants-self-documenting]], `tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`,
`tasks/reference/lean-ga-proof-architecture.md` (the A/B/C judgment + "objects in, scalars in the body").
