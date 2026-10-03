# Lift Lean theorem statements from coordinate tuples to GA objects + named relations

**Status:** proposed — needs go-ahead
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

## Open questions

None blocking — ready to start on go-ahead.
