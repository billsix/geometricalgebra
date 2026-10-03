# Lift Lean theorem statements from coordinate tuples to GA objects + named relations

**Status:** done (first increment; remainder judged unnecessary). **Priority:** 5. **Difficulty:** 6.
**Completed:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).

Finished the coordinate-free migration in the laggard G2 proofs, where theorems were still stated over
raw real coefficients and asserted geometric facts by reading struct fields. The target example
(the maintainer's note) was `G2.dual_vec_perp`, `(mul (dual (vec x y)) (vec x y)).s = 0` — a
perpendicularity fact poking `.s`.

Done (option B — the maintainer's choice among the dot-home options):

- Added `proofs/GacalcProofs/Predicates2D.lean` (imports `Versor2D`, where `G2.dot` lives) with
  `dual_perp {v : G2} (hv : IsVector v) : dot (dual v) v = 0` — "the dual of a vector is perpendicular
  to it," stated through the named `dot` over an `IsVector` object. The coordinate `dual_vec_perp`
  stays in `G2.lean` as the leaf it rests on.
- Consequent to the naming rule, this made "predicates" a paired concept, so
  `Predicates.lean → Predicates3D.lean` (sibling of the new `Predicates2D.lean`); root import updated.

Classification (from reading `G2.lean`): the rest of G2's coordinate-tuple theorems are **genuine
leaves** and were left as-is — the mul-table, `normSq_vec`, `vec_mul` (the coordinate product bridge),
`dual_vec`, `I_sq`/`I_sq_eq_sign`, `reverse_vec`, and `dot_is_sym_part`/`wedge_is_antisym_part`/
`dot_eq_coord_sum` (these *define* dot/wedge in coordinates — the bridge layer's job; maintainer
confirmed: leave as leaves). So after lifting `dual_vec_perp` there was nothing else worth lifting.

Verified `make lean` green (`Predicates2D` and `Predicates3D` both built, no `sorry`/`admit`).
Convention recorded in `tasks/reference/lean-ga-proof-architecture.md` ("G2 `dot`/perpendicularity").
