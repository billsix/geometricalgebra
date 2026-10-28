# Lift G2's coordinate-leaking theorem conclusions to G3's object-out form

**Status:** done — 2026-10-28. `make lean` green (8958 jobs; completeness gate OK). Three G2 theorems
lifted to object-equality form matching their G3 twins; the deliberate coordinate cases kept.
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Some `G2.lean` theorems took geometric objects in (`{a b : G2} (ha : IsVector a) …`) but **concluded
with a raw coordinate expression / literal**, where the `G3.lean` twin concludes about the object —
violating the house rule *"geometric objects in, scalars in the body, geometric objects **out**"*
(`CLAUDE.md`, `tasks/reference/lean-ga-proof-architecture.md`). Audited all of G2 (maintainer's "lift
every genuine case") and lifted the three genuine cases to their G3-twin object form; verified `make
lean` green. No consumer needed updating — the three had only doc-comment mentions, no `rw`/`simp`
call sites.

## What was done (`proofs/GacalcProofs/G2.lean`)

Three conclusions lifted (object form, matching G3; proofs gained `dot`/`one`/`wedge`/`neg` in the
`simp only` set and an `ext <;> ring`):

| theorem | before (leaked) | after (object) |
|---|---|---|
| `dot_is_sym_part` | `(smul (1/2) (add (mul a b) (mul b a))).s = a.c1*b.c1 + a.c2*b.c2` | `smul (1/2) (add (mul a b) (mul b a)) = smul (dot a b) one` |
| `wedge_is_antisym_part` | `(smul (1/2) (sub (mul a b) (mul b a))).c12 = a.c1*b.c2 - a.c2*b.c1` | `smul (1/2) (sub (mul a b) (mul b a)) = wedge a b` |
| `I_sq` | `mul I I = ⟨-1, 0, 0, 0⟩` | `mul I I = neg one` |

The object forms are *strictly stronger* (they pin every component, not just `.s`/`.c12`), and each is
exactly what its docstring already promised.

## Audit: what was deliberately kept coordinate

- **`dot_eq_coord_sum`** — the deliberate "equivalence to the general case" bridge (`(mul a b).s =
  a.c1*b.c1 + a.c2*b.c2` = the Euclidean dot / Mathlib `inner`); its whole point is the coordinate sum.
  Kept (per the decision).
- **Reals-in coordinate leaves** (A/B/C "C-keep"): `vec_mul`, `dot_vec`, `normSq_vec`,
  `normSq_wedge_vec`, `normSq_eq_sum_sq`, `dual_vec_perp`, and `I_sq_eq_sign` (`(mul I I).s =
  (-1)^(r(r−1)/2)` is *about* the scalar part's sign by design — G3's twin is identical). Their inputs
  are free reals / their RHS *is* coordinate arithmetic.
- **The `eq_…_of_is…` bridges** (`eq_vec_of_isVector`, `eq_smul_one_of_isScalar`,
  `eq_smul_e12_of_isBivector`) — they mention coordinates because expressing the object *by* its
  coordinates is their job.
- **`wedge_self_vec` and `wedge_isVector_isBivector_eq_zero`** — conclude `= (⟨0,0,0,0⟩ : G2)`. G3's
  twins use `zero`, but G2 has **no `zero`** (the sibling task
  [[lean-basis-constants-self-documenting]] deliberately did not add one). Left as the `⟨0,0,0,0⟩`
  literal; not a component-arithmetic leak, just the zero value. (If a `G2.zero` is ever added, these
  two could use it.)

## Files touched

- `proofs/GacalcProofs/G2.lean` — the three lifts (statements + proofs + docstrings). Diff is those
  three theorems only; no other declaration changed.

See also: [[lean-basis-constants-self-documenting]], `tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`,
`tasks/reference/lean-ga-proof-architecture.md` (the A/B/C judgment + "objects in, scalars in the body").
