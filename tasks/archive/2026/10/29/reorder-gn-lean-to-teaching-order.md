# Reorder G1/G2/G3 Lean files to the math-teaching order (no functional change)

**Created:** 2026-10-28 · **Completed:** 2026-10-29 (William Emerison Six <billsix@gmail.com>)

Work commit subject: "proofs: reorder G1/G2/G3 to the math-teaching order; fold AlgebraLaws in".

The from-scratch GA proof files introduced concepts in an order that did not match how a student
is taught algebra: `G2.lean`/`G3.lean` defined the geometric product `mul` *before* addition, and
the algebra laws (associativity, distributivity, identity, the scalar laws, orthogonal-vector
anticommutativity) were hoisted out into a shared `AlgebraLaws.lean` instead of living with each
algebra. This work **reordered and relocated** declarations in `G1.lean`/`G2.lean`/`G3.lean` so
they mirror the canonical teaching sequence in `tasks/reference/algebra-teaching-order.md` (companion:
`tasks/reference/openstax-math-pedagogy.md`), **without changing any statement, proof, or name**.
Each file reads top-to-bottom in teaching order, the dead `Versor2D` import is gone,
`AlgebraLaws.lean` was deleted (its laws folded into each algebra), and the proved-theorem set is
unchanged — `make lean` green before and after.

## What was done

A pure relocation — no statement, proof, or name changed.

- **Operations reordered** in `G1`/`G2`/`G3`: `add`/`sub`/`neg`/`smul` were moved to precede
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
  `PlaneRotation3D`, `Rotor`, `Sandwich`, `StudentTrigForms`. Each directly imports both `G2`
  and `G3` — the coverage `AlgebraLaws` had re-exported — so no importer was stranded.
- **`G1` kept its laws inline** and served as the section template: its `mul_comm`/`mul_assoc`/
  `one_mul`/`mul_add` already lived with the algebra; only its operation order was adjusted so it
  exemplifies the teaching order it anchors.
- **No new named addition lemmas** were added (the addition laws stay implicit via `ext <;> ring`),
  keeping this a true no-op refactor.

## Target order (per file), from `tasks/reference/algebra-teaching-order.md` Part II

1. Representation scaffolding (the coordinate `structure`, `@[ext]`, `zero`/`one`, basis blades,
   `vec`/`scalar` constructors, `I`) — notation first, stayed at the top.
2. **Addition & subtraction** and their vector-space siblings: `add`, `sub`, `neg`, `smul`.
3. **The geometric product** `mul`, the **wedge**, and the **dot**.
4. **Reverse and magnitude.**
5. **The algebra laws** with the product: associativity, left/right distributivity, multiplicative
   identity, the scalar laws.
6. The multiplication table, dot/wedge-as-parts, predicates, and the vector-level results, in the
   existing dependency order.

Before the work (measured 2026-10-28), `G2.lean` and `G3.lean` ran basis/constants → `mul` → `wedge`
→ `dot` → `add`/`sub`/`neg`/`smul` → reverse → magnitude → …; `G1.lean` was closest to teaching order
and already kept its laws inline; `AlgebraLaws.lean` held `G2` then `G3` namespaces with `mul_assoc`,
`mul_add`/`add_mul`, `one_mul`/`mul_one`, the `smul`/`scalar_mul` laws and `vec_anticomm_perp`.

Reordering is safe in Lean as long as every declaration's dependencies precede it, and nothing was
renamed or re-namespaced, so relocating a `G2`-namespace theorem from `AlgebraLaws.lean` into
`G2.lean` is invisible to importers. The only hazard was an import cycle.

## How it was done (each phase ended with `make lean`)

- **Baseline:** `make lean` green (8958 jobs), and the sorted theorem/def-name multiset across the
  four files (232 names) captured as the mechanical "before".
- **Dead import:** `AlgebraLaws.lean`'s `import GacalcProofs.Versor2D` named no `Versor2D` symbol;
  as `Versor2D` imports `G2`, it was the only apparent cycle risk. It went with the file.
- **Reorder** the operations blocks in each Gn file by verbatim relocation of whole declarations.
- **Fold `AlgebraLaws.lean`:** a delete-and-rebuild confirmed every moved law's dependencies were
  satisfied at its new location — none needed a later module, so nothing had to stay shared.
- **Verify** (below).

## What stayed separate — the case that was weighed

The maintainer invited the case for keeping some things separate:

- **A law with a forward dependency** would have had to stay out of `G2.lean`; the delete-and-rebuild
  found **none**.
- **Facts framed "G2 and G3 side by side"** could have justified a small shared file; per decision 1
  everything was folded in, and the parallel "### The algebra laws" sections carry the contrast.
- **The representation scaffolding** stayed at the top of each file.

## Verification (equivalence)

- `make lean` green before (8958 jobs) and after (8957 — one fewer, exactly the removed
  `AlgebraLaws` module), with no `sorry`/`admit` in sources.
- The sorted declaration-name multiset across `G1`/`G2`/`G3` was identical (232 = 232): nothing was
  added, removed, or renamed.
- No dangling `AlgebraLaws` references remained in `proofs/` or the live reference docs (inbound
  pointers in `proofs/README.md` and `tasks/reference/*` were repointed in the work commit).
- Only `proofs/` changed, so the Python gates (`make test`/`make format`) were not exercised.

The durable record is `tasks/reference/algebra-teaching-order.md` §Part III.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-29)

The maintainer gave the go-ahead by settling three questions, all per the recommendations:

1. **Scope of `AlgebraLaws.lean`** → fold it entirely into `G2`/`G3` and delete it.
2. **Named addition laws** → reorder existing declarations only; no new `add_comm`/`add_assoc`
   lemmas (the files prove those facts implicitly via `ext <;> ring`). Adding them was left as a
   possible separate follow-up.
3. **G1 as the template** → yes; `G1`'s own operation order was brought into line too.
