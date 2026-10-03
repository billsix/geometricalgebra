# Lift Lean theorem statements from coordinate tuples to GA objects + named relations

**Status:** first increment DONE (option B), `make lean` green, staged. The note-2 example
(`dual_vec_perp`) is lifted; the broader note-1 object-lift of other G2 structural theorems remains
(most of what's left in G2 is genuine leaves — see Investigation). Reopen/continue for any further
lifts, otherwise archivable.
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>, stream-of-consciousness notes).
**Part of:** the Lean proof initiative, `tasks/investigate-lean-proofs-for-ga.md`.
**See also:** `tasks/reference/lean-ga-proof-architecture.md` (the leaf-vs-structural split this task
must respect), `tasks/reference/lean-for-gacalc.md`; the completed coordinate-free sweep
`tasks/archive/2026/09/30/lean-proofs-make-coordinate-free.md` (this task finishes that transition
in the files it did not reach).

## BLUF

Many Lean theorems — especially in `proofs/GacalcProofs/G2.lean` — are still stated over raw real
coefficients (`theorem vec_mul (u1 u2 v1 v2 : ℝ) …`) and assert geometric facts by poking struct
fields (`(mul (dual (vec x y)) (vec x y)).s = 0`). The coordinate-free sweep already converted most
of `G3.lean`, `AlgebraLaws.lean`, `StandardPosition.lean`, `Projection*.lean` to typed-object
statements (`(u v : G3)`, `IsVector`, `dot a b`, `perp_iff_mul_eq_wedge`). This task finishes that
migration for the laggard files: restate the *structural/derived* theorems over GA objects (typed
arguments, component access via `.`/accessors) and express relationships through the **named
relations that already exist** (`dot`, `perp`, `cosine`) instead of bare coordinate equalities —
**while leaving the intentional coordinate leaf layer in place**. "Done" = the targeted theorems
read as GA statements, `make lean` is green and `sorry`-free, and the leaf lemmas they now rest on
are explicitly labeled as such.

## Context — how to read this cold

gacalc's Lean corpus (`proofs/GacalcProofs/*.lean`, gated by `make lean`) is an independent oracle
for the GA *mathematics*. `tasks/reference/lean-ga-proof-architecture.md` defines a deliberate
**leaf-vs-structural** architecture:

- **Leaf lemmas** bridge an operation to the 8-field coordinate struct and are proved by
  `ext <;> ring` / `simp only [...]; ring`. These are *supposed* to be stated in coordinates — e.g.
  `vec_mul` (`G2.lean:149`), `normSq_vec`, `dot_vec` are the bridge from the abstract op to the
  struct. Do **not** delete these.
- **Structural theorems** sit above the leaves and should be coordinate-free `rw` chains over typed
  objects.

The corpus is **mid-transition**. Already object-level (keep as the model): `G3.lean`
(`mul_eq_dot_add_wedge {a b : G3} (ha : IsVector a) …`, `dot (a b : G3)`), `Predicates.lean`
(`perp_iff_mul_eq_wedge`), `AlgebraLaws.lean`, `StandardPosition.lean`, `Projection2D.lean`
(`mul_eq_dot_add_wedge {a b : G2}`, `mul_eq_wedge_of_perp`). Lagging (the targets): **`G2.lean`**
most of all, and any residual coordinate-tuple *structural* theorems elsewhere.

G2 already has the building blocks to lift onto: `IsVector (a : G2)` (`G2.lean:156`),
`eq_vec_of_isVector` (`:159`), `vec_eq_smul` (`:125`). G2 does **not** yet have a `dot (a b : G2)`
free predicate at module scope the way G3 does (`G3.lean:164`) nor a G2 `perp` predicate — note
`Versor2D.lean:25` defines a local `dot (a b : G2)`. Adding a G2 `dot`/`perp` (mirroring G3's
`Predicates.lean`) is the prerequisite for note-2-style restatements and is in scope here.

## The two facets (from the maintainer's notes)

1. **Typed-object arguments + accessor RHS.** Where a theorem is structural, change
   `theorem foo (u1 u2 v1 v2 : ℝ) : mul (vec u1 u2) (vec v1 v2) = ⟨…⟩` to take the vectors (as
   `IsVector` objects, or the specialized typed objects) and access components with `.`. Example
   target: the callers/derived consequences of `vec_mul` (`G2.lean:149`) — `vec_mul` itself is
   plausibly a genuine leaf and may stay, but its *use sites* should speak objects.
2. **Named relations instead of field-poking.** `dual_vec_perp` (`G2.lean:208`),
   `(mul (dual (vec x y)) (vec x y)).s = 0`, states a *perpendicularity* fact by reading `.s`.
   Restate it as "the dual of a vector is perpendicular to it" via a G2 `perp`/`cosine` predicate
   (the G2 analogue of `perp_iff_mul_eq_wedge`), with the `.s = 0` kept only as the leaf the
   predicate unfolds to. Reuse `dual_vec` (`G2.lean:203`).

## Method (respecting the architecture)

1. Inventory every `theorem … (… : ℝ)` in the lagging files; classify each **leaf** (keep, label it
   as the coordinate bridge in its docstring) vs **structural** (lift).
2. Add the small missing G2 primitives (`dot`, `perp`/`cosine` predicate) mirroring G3.
3. Lift the structural theorems; keep each resting on a thin, named leaf.
4. `make lean` green + `sorry`-free after each file. Prefer small per-file commits.

## Decisions (resolved 2026-10-03, William Emerison Six <billsix@gmail.com>)

1. **`vec_mul` stays a coordinate leaf**; only its consequences / use sites are lifted. (Confirms the
   leaf/structural boundary for the ambiguous core-product lemmas: the raw coordinate bridge stays.)
2. **Notes 1 and 2 stay merged** in this one task (object-level statements + named relations are one
   initiative), including adding the small missing G2 `dot`/`perp` predicate.
3. Scope stays `G2.lean` + any residual coordinate-tuple *structural* theorems; the `Lagrange.lean` /
   `Trig.lean` coordinate `ring` leaves are **out** (they are the intentional leaf layer).

## Investigation (2026-10-03) — a structural prerequisite surfaced; NOT started

Read `G2.lean` in full to plan the lift. Classification of its coordinate-tuple theorems:

- **Genuine leaves (keep in coordinates):** `normSq_vec`, `vec_eq_smul`, the mul-table
  (`e_1_sq`/`e_2_sq`/`e_1_mul_e_2`/`e_2_mul_e_1`/`e_12_sq`), `vec_mul` (per the decision above),
  `I_sq`/`I_sq_eq_sign`, `dual_vec`, `reverse_vec`. These are the bridge layer; they stay.
- **The clean structural win:** `dual_vec_perp` (`G2.lean:208`) — "the dual of a vector is
  perpendicular to it," currently stated as `(mul (dual (vec x y)) (vec x y)).s = 0`. Lifting it to a
  `dot`/`perp`-named, `IsVector`-object form is exactly the maintainer's note-2 example.

**Blocker found (why I did not just do it):** lifting `dual_vec_perp` needs a `dot`/`perp` for G2
reachable from `G2.lean` — but **`G2.dot` already exists, defined in `Versor2D.lean`** (`:25`), along
with a full dot algebra there (`dot_comm`, `dot_add/sub/smul_left/right`, `dot_eq_coord`).
`G2.lean` imports only `Mathlib`, so it **cannot** reference `Versor2D`'s `dot` (that's the wrong
direction — `Versor2D` imports `G2`). So the lift requires a **dot-home decision** with cross-file
blast radius, which is a structural choice for the maintainer, not a 1am unilateral move. Options:
  - (A) **Promote `dot` (and its algebra) from `Versor2D.lean` into `G2.lean`** (the core file
    everything imports), and have `Versor2D` use it. Cleanest canonical home; touches `Versor2D` and
    must re-verify all `G2.dot` users (many files).
  - (B) **Move `dual_vec_perp` out of `G2.lean`** into a new `Predicates2D.lean` (mirroring G3's
    `Predicates.lean`) that imports `Versor2D`, and state it there via `dot`/`perp`. Keeps `G2.lean`
    as pure leaves; adds a file (consistent with the topic-file convention).
  - (C) define a second G2 `dot` in `G2.lean` — **rejected** (duplicate definition, conflicts).

This is the lift's natural first step and it gates the note-2 restatements, so the task is **held on
that decision** rather than started. The note-1 object-lifts of other G2 structural theorems can
proceed independently of the dot decision, but most of G2's remaining coordinate theorems are the
leaves above, so the practical surface of this task is smaller than it first looked — it is largely
"pick a dot home, then restate `dual_vec_perp` (and any perpendicularity facts) via it."

## Implemented (2026-10-03, option B, `make lean` green, staged)

Dot-home decision: **(B)** (maintainer approved). Done:

- New `proofs/GacalcProofs/Predicates2D.lean` (imports `Versor2D`, namespace `GacalcProofs.G2`) with
  `dual_perp {v : G2} (hv : IsVector v) : dot (dual v) v = 0` — "the dual of a vector is
  perpendicular to it," stated through the named `dot` over an `IsVector` object. The coordinate leaf
  `G2.dual_vec_perp` stays in `G2.lean` as the bridge.
- **Naming-consistency consequence of the approved cleanup rule:** adding a 2D predicates file makes
  "predicates" a *paired* concept, so `Predicates.lean` → **`Predicates3D.lean`** (sibling of
  `Predicates2D.lean`). Only root `GacalcProofs.lean` imported it (now imports both). Verified green
  (both `Predicates2D` and `Predicates3D` built; no `sorry`/`admit`).

**What remains (not done):** the broader note-1 lift of other G2 coordinate-tuple *structural*
theorems. Per the Investigation, most of G2's remaining coordinate theorems are genuine leaves
(mul-table, `normSq_vec`, `vec_mul`, `dual_vec`, `I_sq*`, `reverse_vec`) that stay; the practical
remaining surface is small. `dot_is_sym_part` / `wedge_is_antisym_part` / `dot_eq_coord_sum` could be
given `dot`-named object companions if desired, but they are borderline leaf (they *define* dot/wedge
in coordinates) — a judgment call left for an attended pass.

## Open questions

None blocking. Optional, for a later pass: do you want `dot`-named object companions for
`dot_is_sym_part` / `wedge_is_antisym_part` (note-1 continuation), or are those fine as coordinate
leaves? My read: fine as leaves.
