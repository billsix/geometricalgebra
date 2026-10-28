# Audit where each Lean declaration is defined and in what order; move each to its logical home, then reorder

**Status:** proposed — needs go-ahead.
**Priority:** 7
**Difficulty:** 7
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

Go through `proofs/GacalcProofs/*.lean` (~32 files) and fix the structure along **two axes**:

1. **Which file each declaration lives in — its *logical home*.** Core algebra operations belong in the
   algebra-core file (`G1.lean`/`G2.lean`/`G3.lean`); concept-specific results belong in their concept
   file (`Projection*`, `Rotation*`, `Sandwich`, …). Move the misplaced ones.
2. **The order of declarations *within* each file** — a consistent, readable top-to-bottom story that
   still respects Lean's top-down name resolution.

**The motivating example (maintainer, 2026-10-28):** `G2.dot` is defined in `Versor2D.lean` and
`G2.wedge` in `Projection2D.lean`, even though `dot`/`wedge` are the two parts of the geometric product
— core algebra — and `G3` **already** defines both in `G3.lean` (`dot` at `G3.lean:164`, `wedge` at
`G3.lean:68`). `G2`'s should move into `G2.lean` to match, and that generalizes: **`dot`, `wedge`, and
the other core operations should be defined in `G2`/`G3`.** This task finds every such case, not just
this one.

The deliverable is a **content-preserving** reorganization: `make lean` stays green and `git diff` shows
only relocations (plus any `/-! ### … -/` section headers added to make the new grouping legible) — no
definition, statement, or proof body changed. (To be done **last** of the current three-task run.)

## Context (cold start)

- The proofs live in `proofs/GacalcProofs/` (`make lean` builds + verifies them; needs a `USE_LEAN=1`
  image). Architecture, techniques, the leaf-vs-structural layering, and the by-topic file inventory are
  in `tasks/reference/lean-ga-proof-architecture.md` — **read it first**; it is the backbone the ideal
  structure should express, and it will need updating when this task moves things (see below).
- **The current `dot`/`wedge` placement is a *documented* decision this task reverses.** The
  architecture doc states: "`G2.dot` (and its bilinearity algebra) lives in `Versor2D.lean`, not
  `G2.lean` (which imports only Mathlib)." The stated rationale — keep `G2.lean` Mathlib-only — does
  **not** actually force `dot`/`wedge` out: `G2.dot a b := (mul a b).s` and `G2.wedge` are pure
  coordinate formulas depending only on `mul`/`smul`/`vec`/fields, all already in `G2.lean`. So the move
  is import-safe. Confirmed by reading `Versor2D.lean:23–57` (the whole `dot` cluster: `dot`,
  `dot_sub/add/smul_left/right`, `dot_comm`, `dot_vec` — every proof is `simp only [dot, mul, …]; ring`,
  no Mathlib dependence beyond `ℝ`) and `Projection2D.lean:15–81` (the `wedge` cluster: `wedge`,
  `wedge_sub/add/smul_left/right`, `wedge_self_vec`, `wedge_antisymm`, `normSq_wedge_vec` — same shape).
- **Hard constraint — Lean resolution is top-down, within and across files.** A `def`/`theorem` must
  appear textually *above* its uses within a file, and a file must be *imported* before its names are
  used. So a move is legal only if it keeps every user below its dependencies and the import graph
  acyclic. Moving `G2.dot`/`G2.wedge` *up* into `G2.lean` is safe (G2.lean is imported by everything);
  moving something *down/out* of a core file into a concept file is only legal if nothing in the core
  file (or another core-importing file that doesn't import the concept file) uses it.

## The rubric (decide once, apply uniformly)

**Axis 1 — logical home (which file).** A declaration belongs in the **algebra-core file** (`G2`/`G3`)
when it is part of the algebra itself: the `structure`, the elementary ops (`add`/`sub`/`neg`/`smul`/
`mul`/`wedge`/`reverse`), `dot`, basis elements/constructors, `normSq`/`magnitude`, the multiplication
table, the core bilinearity **leaf lemmas** for `mul`/`dot`/`wedge`, the fundamental split
`mul_eq_dot_add_wedge`, `dot_is_sym_part`/`wedge_is_antisym_part`, and the grade **predicates** with
their bridges. It belongs in a **concept file** when it is *about* a built-on concept (projection,
rejection, a specific versor/rotor construction, rotation, reflection, cross, measures, contractions,
the Mathlib equivalence) rather than the raw algebra. Judgment call per declaration; when a leaf lemma
is used by several concept files, it is core (shared leaves go home to the core). Record each move.

**Axis 2 — within-file order.** Among the valid topological sorts of the in-file dependency DAG, choose
the one reading **vocabulary-before-grammar**: (1) module docstring + `namespace`; (2) the `structure`;
(3) the **basis elements / constants** (`one`/`e_1`/`e_2`/`e_12`/`I`) and constructors (`vec`) — the
values that name the space, right after the `structure`; (4) the elementary **operations**
(`add`/`sub`/`neg`/`smul`/`mul`/`wedge`/`reverse`); (5) `normSq`/`magnitude`; (6) multiplication table +
core leaf lemmas, grouped by operation under `/-! ### … -/` headers; (7) the split + sym/antisym parts;
(8) predicates, each with its `eq_…_of_is…` bridge + `is…_…` constructor right after it; (9)
duals/pseudoscalar; (10) equivalence-to-general / Mathlib-bridge material last. Dependency order wins
wherever it conflicts with the narrative; note each bend. (Basis-before-operations per the maintainer,
2026-10-28: the docstring introduces the basis first, so the file should too.)

**Seed finding (maintainer, 2026-10-28):** in `G2.lean` today the basis constants `one`/`e_1`/`e_2`/
`e_12` sit at lines ~87–98, *after* `mul`/`add`/…/`reverse` — they belong at stage (3) above, right
after `structure G2` and before the operations. A concrete first case for Axis 2. (Legal: the constants
are struct literals depending on nothing, and the operations don't reference them, so either order
type-checks — this is a readability move, not a dependency one.)

## Method

1. **Build the cross-file declaration map first.** For every top-level `def`/`theorem`/`abbrev`, record
   (name, current file, in-file dependencies, cross-file dependencies, who uses it). A `tools/`/adhoc
   script that greps declaration headers + a reverse-reference scan is the honest way (log the map under
   `tasks/adhoc/<slug>/data/`). This map decides both axes and proves which moves are legal.
2. **Decide each declaration's home** per Axis 1; list the planned moves (from-file → to-file) and
   confirm each is import-legal against the map.
3. **Move cross-file clusters first** (e.g. the whole `G2.dot` cluster `Versor2D → G2`, the `G2.wedge`
   cluster `Projection2D → G2`), updating any now-redundant `import`/`open` lines. `make lean` after each
   cluster.
4. **Then reorder within each file** per Axis 2, moving whole declaration blocks (docstring + signature
   + proof as one unit); add `/-! ### … -/` headers for the new grouping. `make lean` after each file.
5. **Verify content-preservation mechanically.** The change must be relocations + headers only: extract
   the set of declaration bodies before vs. after and diff it (identical set ⇒ no body changed), plus
   `make lean` green. Commit per file/cluster as a quick-save so a bad move is one `git reset` away.
6. **Update the architecture doc** (`tasks/reference/lean-ga-proof-architecture.md`): reverse the
   "`G2.dot` lives in `Versor2D`" note, and record the finalized home-file + within-file rubric so future
   files are authored right from the start. Fix any prose pointer that cites a moved declaration's file.

## Open questions

1. **Scope of cross-file moves.** Recommend: move anything whose logical home is unambiguous *and*
   import-legal (the `dot`/`wedge`→core cases, plus whatever the map surfaces); for a declaration whose
   home is genuinely debatable, leave it and log it as a finding rather than guess. Confirm.
2. **One rubric for all files, or per-family?** (algebra-core `G1/G2/G3` vs. concept files vs.
   `MathlibBridge`). Recommend: one rubric, concept files omitting the stages they lack. Confirm.
3. **Section headers.** Adding `/-! ### … -/` headers is strictly new comment lines (a content
   addition). Recommend: allowed as the mechanism that makes the order legible, called out separately in
   the commit. Confirm.
4. **G1 parity.** `G1.lean` already holds its own `dot`/`wedge`. Fold G1 into the same normalization so
   all three algebra-core files have the same shape? Recommend: yes. Confirm.

## Deliverables

- Each touched file at its logical-home + ideal-order shape; `make lean` green; `git diff` reviewed to
  confirm relocations (+ headers) only — no proof/statement/def body changed.
- The cross-file move list + per-file order record kept in this task doc (harvested before squash).
- The home-file + within-file rubric harvested into `tasks/reference/lean-ga-proof-architecture.md`, and
  the stale "`G2.dot` in `Versor2D`" note corrected there.
