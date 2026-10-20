# Lean sweep: find ℝ-scalar statements that should be geometric-object statements

**Status:** done 2026-10-20 — recon complete; the one clean A-site lifted and verified
(`make lean` green, sorry-free); the rest classified C/B/borderline per the approved recommendation.
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-10-19 (William Emerison Six <billsix@gmail.com>: "sweep the lean proofs and find
places where Real numbers are used that really could use geometric objects like g2 and g3")
**Done:** 2026-10-20 (William Emerison Six <billsix@gmail.com>: "I go with your recommendations")

## BLUF

Continuation of the 2026-10-04 polynomial-tier object-lift (the house rule "Coordinates only when
needed / geometric objects in, scalars in the body, geometric objects out"). Walked every `ℝ`-binder
site in `proofs/GacalcProofs/*.lean` and classified each A (lift to object) / B (keep as a bridged
`_coord` leaf) / C (genuine scalar or definitional unfold). The corpus was **already mostly swept in
2026-10-04**, so the one clean, unambiguous A-site remaining was **`G2.vec_anticomm_perp`** — its `G3`
twin was already object-form and the `G2` version was the lone leftover in free `ℝ` coords, with zero
consumers. Lifted it; `make lean` green, no new `sorry`/`admit`. Everything else is C or B, with a
short **borderline** list left for a per-site call (not converted), per the approved recommendation.

## Result

**Converted (A) — 1 site.** `G2.vec_anticomm_perp` (`AlgebraLaws.lean`): was
`(u1 u2 v1 v2 : ℝ) (h : u1*v1+u2*v2 = 0) : mul (vec u1 u2) (vec v1 v2) = neg (mul (vec v1 v2) (vec u1 u2))`,
now `{u v : G2} (hu : IsVector u) (hv : IsVector v) (h : dot u v = 0) : mul u v = neg (mul v u)` —
matching the existing `G3.vec_anticomm_perp` twin exactly. No consumers to update (the only caller,
`StudentTrigForms`, already uses the `G3` object form). The proof stays coordinate (obtain the
`IsVector` zero-fields, `simp only [dot, mul, <zeros>]`, `ext`, `linear_combination 2*h` / `ring`);
needed `import GacalcProofs.Versor2D` for `G2.dot` (acyclic — `Versor2D` imports only `G2`). Verified:
`make lean` → `Build completed successfully`, `[lean] no sorry/admit`, `[lean] OK`.

**Left as C/B (not converted).** The overwhelming majority: `smul`/`smul_smul` scalars; every angle /
`cos`/`sin` theorem (`rot`, `uvec`, `polar`, `planeRotor`, `fullAngleRotor`, `rotXY/XZ/YZ`, …); the
definitional `vec`/`bivector`/`trivector` unfold leaves (`normSq_vec`, `dot_vec`, `cross_vec`,
`vec_mul`, `isVector_vec`, …); `lagrange_2d/3d` pure-real identities; and every already-bridged
`_coord` leaf still shared ≥2× by object theorems (`CrossStandardPosition`, `Projection3D`,
`ProjectionRotation3D`, `Rotation3D`, `Sandwich`, `Versor2D`, `StandardPosition2D`, `TrigEquiv`) —
the sanctioned pattern, left in place.

**Borderline — listed for a per-site call, NOT converted (recommendation, approved):**
- `Exp.lean` `expBivectorGeneral (p q r : ℝ)` + `normSq_expBivectorGeneral` + `isRotor_expBivectorGeneral`:
  `(p,q,r)` are a bivector's components and the `def` builds `bivector p q r`. Lifting it means a NEW
  object-level `exp (B : G3) (hB : IsBivector B)` def plus its rotor theorems (new theory, not a
  mechanical statement lift — closer to a new project), and there is no object-level Lean `exp` to lift
  into yet. Left as-is; revisit if/when an object-level `exp` is wanted.
- `Projection2D.lean` `vec_wedge_I_eq_zero (x y : ℝ)` / `reject_from_I_eq_zero (x y : ℝ)` and
  `Projection3D.lean` `wedge_reject (a1 a2 a3 : ℝ) (b : G3)`: non-`_coord` scalar-taking theorems that
  *could* take `IsVector` objects, but each is a single-use leaf whose lift buys little.

## See also

- `tasks/reference/lean-ga-proof-architecture.md` — "Coordinates only when needed" (the A/B/C
  judgment) and the leaf-node index (updated: `vec_anticomm_perp` is now object-form in both `G2`/`G3`).
- `tasks/archive/2026/10/04/lean-lift-theorem-statements-to-objects.md` — the polynomial-tier sweep
  this continues; `tasks/reference/lean-proof-corpus-review-2026-10-04.md` — the corpus map.
