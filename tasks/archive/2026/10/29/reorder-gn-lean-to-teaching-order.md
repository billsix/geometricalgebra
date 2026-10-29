# Reorder G1/G2/G3 Lean files to the math-teaching order (no functional change)

**Status:** done — 2026-10-29. William Emerison Six <billsix@gmail.com> gave the go-ahead by
resolving the three open questions (all in favor of the recommendations). Work commit subject:
"proofs: reorder G1/G2/G3 to the math-teaching order; fold AlgebraLaws in".
**Priority:** 5  (a readability/pedagogy refactor; nothing was broken or blocked on it)
**Difficulty:** 4  (pure relocation across 3 large files + the shared-laws file)

## BLUF

The from-scratch GA proof files introduce concepts in an order that does not match how a
student is taught algebra: `G2.lean`/`G3.lean` define the geometric product `mul` *before*
addition, and the algebra laws (associativity, distributivity, identity, the scalar laws,
orthogonal-vector anticommutativity) are hoisted out into `AlgebraLaws.lean` instead of
living with each algebra. This task plans a **reordering + relocation** of declarations in
`G1.lean`/`G2.lean`/`G3.lean` so they mirror the canonical teaching sequence documented in
[[algebra-teaching-order]], **without changing any statement, proof, or name** — `make
lean` must stay green and prove the same theorem set before and after. "Done" = the files
read top-to-bottom in teaching order, the dead `Versor2D` import is gone, and the proved-
theorem set is provably unchanged.

## Outcome (2026-10-29)

Done, as a pure relocation — no statement, proof, or name changed.

- **Operations reordered** in `G1`/`G2`/`G3`: `add`/`sub`/`neg`/`smul` now precede
  `mul`/`wedge`/`dot`, under split section headers "### Addition and the vector-space
  operations" then "### The geometric product, the wedge, and the dot".
- **`AlgebraLaws.lean` folded in and deleted** (question 1 → fold entirely). The G2 laws moved
  into `G2.lean` and the G3 laws into `G3.lean`, each under a new "### The algebra laws" section;
  `vec_anticomm_perp` sits beside each file's wedge/anticommutativity material (it depends on it).
  No law needed a shared file — Phase 3's delete-and-rebuild confirmed every law's dependencies
  are satisfied within its own algebra (no import cycle). The dead `import GacalcProofs.Versor2D`
  vanished with the file (Phase 1).
- **Eight importers repointed** off `AlgebraLaws` onto `G2`/`G3` (the aggregator
  `GacalcProofs.lean` plus ProjectionRotation3D/2D, StandardPosition, PlaneRotation3D, Rotor,
  Sandwich, StudentTrigForms); each now directly imports both G2 and G3, the coverage
  `AlgebraLaws` had re-exported.
- **G1 kept inline** (question 3 → G1 is the section template): its `mul_comm`/`mul_assoc`/
  `one_mul`/`mul_add` already lived with the algebra; only its operation order was adjusted.
- **No new named addition lemmas** (question 2 → reorder existing only). A follow-up task could
  add explicit `add_comm`/`add_assoc` lemmas if ever wanted; not done here.

**Verification (equivalence):** `make lean` green before (8958 jobs) and after (8957 — one fewer,
the removed `AlgebraLaws` module), no `sorry`/`admit`; and the sorted declaration-name multiset
across `G1`/`G2`/`G3` is identical before and after (232 = 232), proving nothing was added,
removed, or renamed. The durable record is [[algebra-teaching-order]] §Part III.

---

Below is the plan as executed (kept as the how-record).

The maintainer explicitly invited the case for keeping some things separate — see §"What stays separate."

## Context (cold-start)

- Read first: [[algebra-teaching-order]] (the teaching order + the ordering principles this
  task applies) and its companion [[openstax-math-pedagogy]].
- Files: `proofs/GacalcProofs/{G1,G2,G3,AlgebraLaws}.lean`, aggregated by
  `proofs/GacalcProofs.lean`. Build/verify with **`make lean`** (runs `proofs/check.sh`:
  `lake build` + a `sorry`/`admit` completeness gate; needs a `USE_LEAN=1` image, the
  default full image). See `tasks/reference/lean-ga-proof-architecture.md`.
- Current ordering, measured 2026-10-28:
  - **G2.lean**: basis/constants → `mul` (~L87) → `wedge` → `dot` → `add`/`sub`/`neg`/`smul`
    (~L106) → reverse → magnitude → multiplication table → dot/wedge-as-parts → …
  - **G3.lean**: same shape (product block before the vector-space ops).
  - **G1.lean**: closest to teaching order already — keeps its own `mul_comm`/`mul_assoc`/
    `one_mul`/`mul_add` inline rather than in `AlgebraLaws.lean`.
  - **AlgebraLaws.lean**: `G2` then `G3` namespaces, each with `mul_assoc`, `mul_add`/
    `add_mul` (+`sub` variants for G3), `one_mul`/`mul_one`, `smul_mul`/`mul_smul`/
    `smul_smul`/`scalar_mul`/`one_smul`, and `vec_anticomm_perp`.
- **Why reordering is safe in Lean:** a Lean file checks regardless of *declaration order*
  as long as every declaration's dependencies precede it, and nothing here renames or
  re-namespaces anything. Relocating a `G2`-namespace theorem from `AlgebraLaws.lean` into
  `G2.lean` is invisible to every downstream importer (they import the namespace, now
  satisfied by `G2` which they already transitively import). The only hazard is an import
  cycle (below), which we check mechanically.

## Target order (per file), from [[algebra-teaching-order]] Part II

1. Representation scaffolding: the coordinate `structure`, `@[ext]`, `zero`/`one`, basis
   blades as elements, `vec`/`scalar` constructors, `I`. (Notation first — no textbook
   analogue; stays at top.)
2. **Addition & subtraction** and their vector-space siblings: `add`, `sub`, `neg`, `smul`.
3. The **addition laws**, stated right here: commutative, associative, additive identity
   (`zero`/`add_zero`), additive inverse (`neg`/`add_neg`). (Currently mostly implicit via
   `ext <;> ring`; add the named lemmas where the teaching order wants them, only if they
   can be stated without forward deps.)
4. **The geometric product** `mul`, then the **product laws** with it: associativity,
   left/right **distributivity** (the bridge property — comes after both ops exist),
   multiplicative **identity** (`one_mul`/`mul_one`), the **scalar** laws
   (`smul_mul`/`mul_smul`/`scalar_mul`/…).
5. The **wedge**, **dot**, reverse, magnitude, the multiplication table, dot/wedge-as-parts,
   predicates, and the vector-level results — in the existing dependency order.
6. `vec_anticomm_perp` beside the product/anticommutativity material it belongs to.

Net effect: §2–3 (addition + its laws) move **above** §4 (product + its laws); the
`AlgebraLaws.lean` G2/G3 content folds into §3–4 of the respective file.

## Plan (phased; each phase ends with `make lean` green)

**Phase 0 — baseline oracle.** Before touching anything, capture the current proved set as
the "before": `make lean` green, and record the list of theorem/def names per file
(`grep -nE '^(theorem|lemma|def|example)' G1 G2 G3 AlgebraLaws`). This is the mechanical
"before" to diff against (per the house rule: derive the before, don't hand-transcribe).

**Phase 1 — delete the dead import.** `AlgebraLaws.lean:3` `import GacalcProofs.Versor2D`
is unused (no `Versor2D` name in its body; verified 2026-10-28). Remove it. This also
removes the *only* apparent G2↔laws cycle risk (`Versor2D` imports `G2`). `make lean`.

**Phase 2 — reorder within each Gn file** (no cross-file moves yet). Move the `add`/`sub`/
`neg`/`smul` block and any addition laws above the `mul`/`wedge`/`dot` block in `G2.lean`
and `G3.lean`, matching G1's shape and the target order above. Pure cut/paste of whole
declarations; `make lean` after each file.

**Phase 3 — fold `AlgebraLaws.lean` into `G2.lean`/`G3.lean`.** Move each `G2`-namespace
law into `G2.lean` at its teaching-order slot (identity/distributive/scalar laws right
after `mul`; `vec_anticomm_perp` by the anticommutativity material), same for `G3`. For
each moved law, **delete-and-rebuild** to confirm its dependencies are satisfied at the new
location; if one genuinely needs a later module, leave it in a shared file (see below) and
note why in a comment. Update `proofs/GacalcProofs.lean`'s import list (drop
`AlgebraLaws` if it empties). `make lean`.

**Phase 4 — verify equivalence.** `make lean` green, and diff the Phase-0 name list against
the new one: the set of proved theorems/defs must be **identical** (only their file/location
changed). Any delta is a bug. Also confirm `grep -r AlgebraLaws proofs/` has no dangling
references (CLAUDE.md, other Lean files, reference docs).

## What stays separate — the case against folding everything in

The maintainer asked to hear this. Candidates to keep in a shared file even after the sweep:

- **Any law with a genuine forward dependency.** Phase 3's delete-and-rebuild is the test:
  if a `G2` law provably needs a module that imports `G2`, folding it in creates a cycle and
  it must stay out. (As of 2026-10-28 the only suspected case — the `Versor2D` import — is
  dead, so *nothing currently known* needs to stay out for this reason; but re-verify, don't
  assume.)
- **Facts that are deliberately "both G2 and G3 in one place" for teaching contrast.** If a
  law is pedagogically clearer stated once for both algebras side by side (as
  `AlgebraLaws.lean`'s header frames associativity/distributivity for G2 *and* G3 together),
  that is a real editorial reason to keep a small shared `AlgebraLaws.lean` — the teaching
  order is a default, not a mandate. Decide per law; default to folding in unless the
  side-by-side framing earns its keep.
- **The representation scaffolding** stays at the top of each file (notation-first), not
  reordered into the "addition" section.

## Verification

- `make lean` green before (Phase 0) and after (Phase 4).
- Phase-0 vs Phase-4 theorem/def-name set identical (the equivalence proof).
- No dangling `AlgebraLaws` references anywhere (`grep -rn AlgebraLaws proofs/ tasks/ CLAUDE.md`).
- This touches only `proofs/` — no Python, no generator, no book; `make test`/`make format`
  are unaffected but cheap to run as a sanity check.

## Open questions — resolved 2026-10-29 (William Emerison Six <billsix@gmail.com>)

1. **Scope of `AlgebraLaws.lean`** → **fold it entirely into `G2`/`G3`.** Done; no law needed a
   shared file — Phase 3's delete-and-rebuild found every law's dependencies satisfied within its
   own algebra (no import cycle). `AlgebraLaws.lean` deleted.
2. **Named addition laws** → **reorder existing declarations only** (no new lemmas; keeps it a
   true no-op refactor). A separate follow-up could add explicit `add_comm`/`add_assoc` named
   lemmas if that faithfulness is ever wanted — not done here.
3. **G1 as the template** → **yes.** `G1.lean`'s layout (laws stated with the algebra) is the
   section template `G2`/`G3` now match; `G1`'s own operation order (`add`/`smul` before
   `mul`/`wedge`) was brought into line too, so it exemplifies the teaching order it anchors.
