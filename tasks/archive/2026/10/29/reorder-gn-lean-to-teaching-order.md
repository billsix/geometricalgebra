# Reorder G1/G2/G3 Lean files to the math-teaching order (no functional change)

**Status:** done — 2026-10-29. William Emerison Six <billsix@gmail.com> gave the go-ahead by
resolving the three open questions (all in favor of the recommendations). Work commit subject:
"proofs: reorder G1/G2/G3 to the math-teaching order; fold AlgebraLaws in".
**Priority:** 5  (a readability/pedagogy refactor; nothing was broken or blocked on it)
**Difficulty:** 4  (pure relocation across 3 large files + the shared-laws file)

## BLUF

The from-scratch GA proof files introduced concepts in an order that did not match how a student
is taught algebra: `G2.lean`/`G3.lean` defined the geometric product `mul` *before* addition, and
the algebra laws (associativity, distributivity, identity, the scalar laws, orthogonal-vector
anticommutativity) were hoisted out into a shared `AlgebraLaws.lean` instead of living with each
algebra. This work **reordered and relocated** declarations in `G1.lean`/`G2.lean`/`G3.lean` so
they mirror the canonical teaching sequence in [[algebra-teaching-order]], **without changing any
statement, proof, or name**. The result: each file reads top-to-bottom in teaching order, the dead
`Versor2D` import is gone, `AlgebraLaws.lean` is deleted (its laws folded into each algebra), and
the proved-theorem set is provably unchanged — `make lean` green before and after.

## What was done

A pure relocation — no statement, proof, or name changed.

- **Operations reordered** in `G1`/`G2`/`G3`: `add`/`sub`/`neg`/`smul` now precede
  `mul`/`wedge`/`dot`, under split section headers "### Addition and the vector-space operations"
  then "### The geometric product, the wedge, and the dot". A student meets addition before
  multiplication (OpenStax *Elementary Algebra 2e* §1.3 before §1.4).
- **`AlgebraLaws.lean` folded in and deleted.** The G2 laws moved into `G2.lean` and the G3 laws
  into `G3.lean`, each under a new "### The algebra laws" section placed right after the
  operations/magnitude block; `vec_anticomm_perp` sits beside each file's wedge/anticommutativity
  material, since its proof depends on it. The dead `import GacalcProofs.Versor2D` the file carried
  vanished with it.
- **Eight importers repointed** off `AlgebraLaws` onto `G2`/`G3`: the aggregator
  `GacalcProofs.lean` plus `ProjectionRotation3D`/`ProjectionRotation2D`, `StandardPosition`,
  `PlaneRotation3D`, `Rotor`, `Sandwich`, `StudentTrigForms`. Each now directly imports both `G2`
  and `G3` — the coverage `AlgebraLaws` had re-exported — so no importer was stranded.
- **`G1` kept its laws inline** and served as the section template: its `mul_comm`/`mul_assoc`/
  `one_mul`/`mul_add` already lived with the algebra; only its operation order was adjusted so it
  exemplifies the teaching order it anchors.
- **No new named addition lemmas** were added (the addition laws stay implicit via `ext <;> ring`),
  keeping this a true no-op refactor.

## Context (cold-start)

- Read first: [[algebra-teaching-order]] (the teaching order + ordering principles this work
  applied) and its companion [[openstax-math-pedagogy]].
- Files: `proofs/GacalcProofs/{G1,G2,G3}.lean`, aggregated by `proofs/GacalcProofs.lean`.
  Build/verify with **`make lean`** (runs `proofs/check.sh`: `lake build` + a `sorry`/`admit`
  completeness gate; needs a `USE_LEAN=1` image, the default full image). See
  `tasks/reference/lean-ga-proof-architecture.md`.
- **Starting state (before this work, measured 2026-10-28):**
  - `G2.lean`: basis/constants → `mul` (~L87) → `wedge` → `dot` → `add`/`sub`/`neg`/`smul` (~L106)
    → reverse → magnitude → multiplication table → dot/wedge-as-parts → …
  - `G3.lean`: the same shape (product block before the vector-space ops).
  - `G1.lean`: closest to teaching order already — kept its own `mul_comm`/`mul_assoc`/`one_mul`/
    `mul_add` inline rather than in `AlgebraLaws.lean`.
  - `AlgebraLaws.lean`: `G2` then `G3` namespaces, each with `mul_assoc`, `mul_add`/`add_mul`
    (+`sub` variants for G3), `one_mul`/`mul_one`, `smul_mul`/`mul_smul`/`smul_smul`/`scalar_mul`/
    `one_smul`, and `vec_anticomm_perp`.
- **Why reordering is safe in Lean:** a file checks regardless of *declaration order* as long as
  every declaration's dependencies precede it, and nothing here renamed or re-namespaced anything.
  Relocating a `G2`-namespace theorem from `AlgebraLaws.lean` into `G2.lean` is invisible to every
  downstream importer (they import the namespace, now satisfied by `G2`). The only hazard was an
  import cycle, which was checked mechanically (see below).

## Target order (per file), from [[algebra-teaching-order]] Part II

1. Representation scaffolding: the coordinate `structure`, `@[ext]`, `zero`/`one`, basis blades as
   elements, `vec`/`scalar` constructors, `I`. (Notation first — no textbook analogue; stayed at
   the top.)
2. **Addition & subtraction** and their vector-space siblings: `add`, `sub`, `neg`, `smul`.
3. **The geometric product** `mul`, the **wedge**, and the **dot**.
4. **Reverse and magnitude.**
5. **The algebra laws** with the product: associativity, left/right **distributivity** (the bridge
   property — after both ops exist), multiplicative **identity** (`one_mul`/`mul_one`), the
   **scalar** laws (`smul_mul`/`mul_smul`/`scalar_mul`/…).
6. The multiplication table, dot/wedge-as-parts, predicates, and the vector-level results — in the
   existing dependency order; `vec_anticomm_perp` beside the product/anticommutativity material.

Net effect: addition moved **above** the product, and the `AlgebraLaws.lean` G2/G3 content folded
into each respective file.

> Note on the addition laws: the teaching sequence puts commutative/associative/identity/inverse of
> addition right after `add`. Per decision 2 below, no **named** addition lemmas were added — the
> files prove those facts implicitly via `ext <;> ring` at each use site. Adding explicit
> `add_comm`/`add_assoc`/… lemmas is a possible follow-up, deliberately out of scope here.

## How it was done (phases, each ending with `make lean`)

- **Phase 0 — baseline oracle.** Captured the "before": `make lean` green (8958 jobs), and the
  sorted theorem/def-name multiset across the four files (232 names) — the mechanical "before" to
  diff against.
- **Phase 1 — delete the dead import.** `AlgebraLaws.lean`'s `import GacalcProofs.Versor2D` named
  no `Versor2D` symbol — a stale import. Since `Versor2D` imports `G2`, it was the only apparent
  G2↔laws cycle risk; it was removed (with the whole file, in Phase 3).
- **Phase 2 — reorder within each Gn file.** Moved the `add`/`sub`/`neg`/`smul` block above the
  `mul`/`wedge`/`dot` block in `G1`/`G2`/`G3` (verbatim relocation of whole declarations), split
  the single operations header into the two headers named above.
- **Phase 3 — fold `AlgebraLaws.lean` into `G2`/`G3`.** Moved each law to its teaching-order slot
  (the laws right after the operations/magnitude block; `vec_anticomm_perp` by the
  anticommutativity material). A delete-and-rebuild confirmed every moved law's dependencies were
  satisfied at its new location — none needed a later module, so none created a cycle and nothing
  stayed in a shared file. Deleted `AlgebraLaws.lean` and repointed its eight importers.
- **Phase 4 — verify equivalence.** `make lean` green; the Phase-0 name multiset diffed identical;
  no dangling `AlgebraLaws` references left in `proofs/`.

## What stayed separate — the case that was weighed

The maintainer invited the case for keeping some things separate. The candidates, and how each
resolved:

- **Any law with a genuine forward dependency** would create a cycle if folded up into `G2.lean`
  and would have to stay out. Phase 3's delete-and-rebuild was the test: **none existed** — every
  `G2`/`G3` law's dependencies live within its own algebra. (The one suspected case, the stale
  `Versor2D` import, was dead.)
- **Facts framed "both G2 and G3 side by side" for teaching contrast** could justify a small shared
  file. Per decision 1, the maintainer chose to fold everything in; the side-by-side framing is now
  carried by the parallel "### The algebra laws" sections in the two files instead.
- **The representation scaffolding** stayed at the top of each file (notation-first), not reordered
  into the addition section.

## Verification (equivalence)

- `make lean` green before (8958 jobs) and after (8957 — one fewer, exactly the removed
  `AlgebraLaws` module), with no `sorry`/`admit` in sources.
- The sorted declaration-name multiset across `G1`/`G2`/`G3` was identical before and after
  (232 = 232), proving nothing was added, removed, or renamed — only each declaration's file and
  in-file position moved.
- No dangling `AlgebraLaws` references remain in `proofs/` or the live reference docs (inbound
  pointers in `proofs/README.md` and `tasks/reference/*` were repointed in the work commit).
- This touched only `proofs/` — no Python, generator, or book — so `make test`/`make format`
  (Python gates) were unaffected and not exercised.

The durable record is [[algebra-teaching-order]] §Part III.

## Decisions — resolved 2026-10-29 (William Emerison Six <billsix@gmail.com>)

1. **Scope of `AlgebraLaws.lean`** → **fold it entirely into `G2`/`G3`.** No law needed a shared
   file (Phase 3 delete-and-rebuild found no cycle); `AlgebraLaws.lean` deleted.
2. **Named addition laws** → **reorder existing declarations only** (no new lemmas; keeps it a true
   no-op refactor). A separate follow-up could add explicit `add_comm`/`add_assoc` named lemmas if
   that faithfulness is ever wanted — not done here.
3. **G1 as the template** → **yes.** `G1.lean`'s layout (laws stated with the algebra) is the
   section template `G2`/`G3` now match; `G1`'s own operation order (`add`/`smul` before
   `mul`/`wedge`) was brought into line too.
