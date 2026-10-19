# Lean sweep: find ℝ-scalar statements that should be geometric-object statements

**Status:** proposed — needs go-ahead (a corpus-consistency sweep; recon is read-only)
**Priority:** 6
**Difficulty:** 5
**Created:** 2026-10-19 (William Emerison Six <billsix@gmail.com>: "sweep the lean proofs and
find places where Real numbers are used that really could use geometric objects like g2 and g3")

## BLUF

Walk every theorem/def in `proofs/GacalcProofs/*.lean` and **find the places that take or
produce bare `ℝ` scalars where the statement is really *about a geometric object*** — a `G1`/
`G2`/`G3` vector, bivector, trivector, or versor — and should take that object (plus a grade
predicate) as input and conclude about objects, dropping to coordinates **only in the body**.
This is the next pass of the house rule already in `CLAUDE.md` ("Coordinates only when needed"
and "Geometric objects in, scalars in the body, geometric objects out"); the **polynomial tier
was swept 2026-10-04** (`tasks/archive/2026/10/04/lean-lift-theorem-statements-to-objects.md`),
so this task is the **continuation into the tiers that pass still left as coordinate statements**.
"Done" = (1) a per-file candidate report classifying every `ℝ`-binder site A/B/C (see Plan),
(2) the conversions the report marks "A — lift to object" applied, each re-verified with
`make lean` green and no new `sorry`/`admit`, and (3) the leaf/`_coord` exemptions recorded in
`tasks/reference/lean-ga-proof-architecture.md`.

**Recon (the find) is read-only and comes first — do NOT edit a proof until the report is
reviewed** (this task is scoped by the maintainer's word "find"; the lift is the follow-on).

## Context (read first)

- **The governing rule is already written.** `CLAUDE.md` › "Coordinates only when needed" and
  "Geometric objects in, scalars in the body, geometric objects out": a theorem takes the
  **object** + a grade predicate (`{a : G3} (ha : IsVector a)`) and concludes about objects; it
  drops to `a.c1`/`a.c12` getters **only in the proof body** (`obtain … := ha; simp only […];
  field_simp; ring`). The inverted shape this sweep removes is **"free scalars in, build the
  object inside"** — `foo (a1 a2 a3 : ℝ) : P (vec a1 a2 a3)`.
- **What is NOT a target (genuine scalars stay scalar).** Per the same rule, leave alone:
  angles and their `cos`/`sin` (`θ`, `α`, `β`, `c`, `s`), a scalar multiple `k`/`smul`, pure-real
  identities (`Lagrange.lean`), and the **definitional `vec`/`bivector`/`trivector` unfold leaves**
  (`normSq_vec`, `dot_vec`, `cross_vec`, `vec_mul`, `isVector_vec`, …) whose RHS *is* coordinate
  arithmetic — those are the bridge leaves listed in the arch doc's "Leaf-node index" and are
  meant to stay coordinate. A named `_coord` leaf is **justified** only when a fragile coordinate
  proof (`set`/`calc`/big `field_simp`) is shared by ≥2 object theorems.
- **Prior art to imitate.** The 2026-10-04 polynomial-tier sweep:
  `tasks/archive/2026/10/04/lean-lift-theorem-statements-to-objects.md` (the lift),
  `lean-object-in-getters-out-proof-style.md` (the proof-style), and the corpus review
  `tasks/reference/lean-proof-corpus-review-2026-10-04.md`. Method, the A/B/C judgment, the
  leaf-node index, and the "paths that DON'T work" for coordinate→object conversion are in
  `tasks/reference/lean-ga-proof-architecture.md` (§ "Coordinates only when needed",
  § "Leaf-node index", § "Converting coordinate proofs to object/getter form — paths that DON'T
  work").
- **Deciding unused-ness is by delete-and-rebuild, never by eyeballing** (`CLAUDE.md`): a name
  absent from the body is not proven unused (`field_simp`/`simp` consume `_ ≠ 0` hyps unnamed);
  Lean only warns on the signature kind. Drop a hypothesis/arg by removing it and rebuilding.

## Candidate sites found in recon (2026-10-19, read-only grep — leads, not verdicts)

Starting worklist (from `grep -nE '(theorem|lemma|def).*: ℝ'` over `proofs/GacalcProofs/*.lean`;
each needs the A/B/C judgment, this is not a conversion list):

- **`AlgebraLaws.lean`** — `vec_anticomm_perp (u1 u2 v1 v2 : ℝ) (h : u1*v1 + u2*v2 = 0)` is the
  clearest **A-candidate**: it is a statement about two perpendicular *vectors*, spelled in 4 free
  scalars + a coordinate dot-zero hypothesis; the object form is `{u v : G2} (hu : IsVector u)
  (hv : IsVector v) (hperp : dot u v = 0)`. (`smul`/`smul_smul` take `k m : ℝ` — genuine scalars,
  **C, leave**.)
- **`CrossStandardPosition.lean`** (25 `ℝ` binders) — the `*_coord` theorems
  (`cross_rotXY_equivariant_coord (c s a1 a2 a3 b1 b2 b3 : ℝ)`, `reduceToPlane_b_in_plane`,
  `rotYZ_aligns_yz`, …) are already **bridged** to object theorems (`cross_rotXY_equivariant
  {a b : G3}`); confirm each `_coord` leaf is still shared by ≥2 object theorems (B, keep) or has
  become a single-use inline (A, fold in). The `rotXY_vec`/`rotYZ_vec` unfold leaves are **C**.
- **`Exp.lean`** — `expBivectorGeneral (p q r : ℝ)`, `normSq_expBivectorGeneral`,
  `isRotor_expBivectorGeneral`: `(p q r)` are the *components of a bivector*; candidate to take
  `{B : G3} (hB : IsBivector B)` and conclude about `B.exp()` being a rotor. Judge A vs B.
- **`G1/G2/G3.lean`** — almost entirely **C** (the `vec`/`bivector`/`trivector` definitions and
  their `*_vec` unfold leaves are the coordinate bridge, by design). Scan only for a non-leaf
  theorem that happens to take scalars.
- **`ProjectionRotation3D.lean` / `Sandwich.lean` / `StandardPosition*.lean` / `Rotation2D.lean`**
  — high `ℝ`-binder counts, but most are angle/`cos`/`sin` (**C**) or already object-stated with a
  coordinate body. These need reading, not grep — flag only genuine "scalars in, build object" shapes.

## Plan

1. **Recon / classify (read-only).** For every `ℝ`-binder site, record file:line, the binder, and
   an **A/B/C verdict**: **A** = lift to an object statement (the target); **B** = keep as a named
   `_coord` leaf (fragile proof shared ≥2×) — note which object theorems consume it; **C** = genuine
   scalar / definitional unfold leaf, leave. Deliver the report in this doc (a table per file).
2. **Report and get go-ahead** on the A-list before editing (Open question 1).
3. **Apply the A-list**, one file per staged unit: rewrite the statement to objects + grade
   predicate, move coordinates into the body via `obtain`/getters, **delete-and-rebuild** to prove
   each dropped scalar/hyp is really unused, `make lean` green per unit, no new `sorry`/`admit`.
4. **If a result has book/Python companions** (per `CLAUDE.md` "three forms"), a *statement* change
   that a book page cites by name must update that citation — check `book/docs/*.rst` for the
   theorem name before renaming/re-signing it.
5. **Record** the final leaf/`_coord` exemptions and any new bridge leaves in
   `tasks/reference/lean-ga-proof-architecture.md`; slim this task to a work record pointing there.

## Open questions

1. Scope of the lift: apply to **every** A-site found, or only the clearly-worth-it ones (e.g.
   `vec_anticomm_perp`, `Exp.lean`'s bivector trio) and leave borderline `_coord` bridges as-is?
   Recommend: convert the unambiguous A-sites, leave every already-bridged `_coord` leaf that is
   still shared ≥2× (it is the sanctioned pattern), and list the borderline ones for a per-site call.

## See also

- `CLAUDE.md` › "Coordinates only when needed" and "Geometric objects in, scalars in the body,
  geometric objects out" — the governing rule.
- `tasks/reference/lean-ga-proof-architecture.md` — A/B/C judgment, leaf-node index, non-working
  conversion paths.
- `tasks/archive/2026/10/04/lean-lift-theorem-statements-to-objects.md` — the polynomial-tier sweep
  this continues; `tasks/reference/lean-proof-corpus-review-2026-10-04.md` — the corpus map.
