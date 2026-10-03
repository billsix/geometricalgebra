# Dead-code audit of the Lean proofs (`proofs/GacalcProofs/`)

**Status:** DONE 2026-10-03 — audit run; **no genuine dead code found** (see Findings). Archivable.
**Priority:** 7. **Difficulty:** 5.
**Created:** 2026-10-03 (William Emerison Six <billsix@gmail.com>).
**See also:** `tasks/reference/lean-ga-proof-architecture.md`; the trigger — the sine/cosine work
(`tasks/prefer-sine-cosine-presentation.md`) surfaced dead coordinate `_dot` helpers (already wired
up there).

## BLUF

Systematically find and remove/wire-up genuinely dead lemmas/defs in the Lean proof corpus. The
headline finding from a first scan: **"zero references" is NOT a dead-code signal in a proof
library** — most un-cited theorems are the *deliberate proven results* (the whole point), so they
must be kept. Dead code here means **orphaned helper machinery**: an intermediate lemma or `def`
that was meant to support a proof but is now bypassed (e.g. a refactor stopped citing it). The
appropriate action per item is judgment, not blanket removal: **wire it up** if it's a useful
primitive that lost its caller (as the `_dot` helpers were), or **remove** only if it is truly
vestigial.

## Method (do it safely)

1. Scan: for each top-level `theorem`/`def` in `proofs/GacalcProofs/*.lean`, count references
   outside its own definition (a one-liner `grep -nE '^(noncomputable )?(theorem|def) '` + a
   per-name `grep -c`). ~60 names come back zero-referenced on the first pass.
2. **Triage each zero-ref name** as one of:
   - **Deliberate result** (a named geometric fact — perpendicularity, rotation preserves length,
     an algebra law, an identity, a coverage-table entry): **KEEP**. These dominate the list
     (`dual_perp`, `area_eq_mag_mul_sin`, `lagrange_2d`, `sandwich_preserves_sin`, `rVectorPart_idem`,
     the inverse lemmas, …).
   - **Orphaned helper** (an intermediate step / bridge / `def` with no caller and no role as a
     stated result): candidate for action. Likely homes from the first scan: `CrossStandardPosition`
     (`reduceToPlane_a_on_e1`, `reduceToPlane_b_in_plane`, `cross_rotXY/XZ/YZ_equivariant`,
     `cross_reduced`, `rotYZ_fixes_e1`), `Sandwich` (`sandwich_ahat`, `sandwich_plane_invariant`,
     `sandwich_sub`, `sandwich_comp`), `RotateComponents`, `Normalize` (`magnitude_normalizeVec`),
     `TrigEquiv` (`cos_between_uvec`), `G2`/`G3` (`eq_vec_of_isVector` — a bridge I stopped using;
     it is documented, so lean toward keep), the `expBivector*`/`normSq_expBivector*` helpers.
3. **Confirm genuinely dead before removing**: a grep-zero is necessary but not sufficient — a lemma
   can be pulled implicitly (`@[simp]`/`@[ext]`/aesop). None of the first-scan candidates are
   `@[simp]`-tagged (checked), but the safe confirmation is **remove → `make lean` → keep removed
   only if still green**, restore otherwise. (This is why the audit is its own careful pass, not a
   rushed mass-delete.)
4. Appropriate action per confirmed-dead item: **wire it up** (give it a caller / make it the cited
   primitive) if it is a useful fact that lost its user; **remove** if truly vestigial. Prefer
   wire-up for anything that is a meaningful primitive.

## Already done (the trigger)

The dead coordinate `_dot` helpers backing the student sine/cosine theorems were wired up (lifted to
object-level + cited) under `tasks/prefer-sine-cosine-presentation.md`. This task covers the rest of
the corpus.

## Findings (2026-10-03 — audit run)

- **Unused `def`s: ZERO.** Every `def` (the machinery — `mul`/`dot`/`wedge`/`cross`/`proj`/the
  rotation defs/`versorFromVectors`/…) is used. No dead machinery.
- **~60 zero-reference `theorem`s — all deliberate results, NOT dead.** Triaged every one by its
  docstring: they are named proven facts (`cross_anticomm_vec`, `normSq_reflectVec`, the `sandwich_*`
  properties, the `exp`-is-a-unit-versor lemmas, `mul_eq_proj_dot_add_reject_wedge` = "the payoff of
  the theme", the area/Lagrange forms, …) or documented **construction steps**
  (`CrossStandardPosition.lean` is a file of standalone reduction-to-standard-position results —
  `reduceToPlane_*`, `cross_rot*_equivariant`, `cross_reduced`, … — none citing each other, by design;
  cf. `reduction-to-standard-position.md`). In a proof library these are the *output*; "no caller" is
  expected and removing them would delete certified GA facts. **No `@[simp]`/`@[ext]` tags**, so the
  grep reference counts are reliable (nothing hidden).
- **The only genuine dead code was the `_dot` helper orphans** created by this session's rename —
  already fixed (lifted to object-level + cited) under `tasks/prefer-sine-cosine-presentation.md`.

**Recommendation: no removals, and no "dead" comments** — nothing in the corpus is junk; it is all
intentional results/machinery. One adjacent, non-dead observation: the `CrossStandardPosition`
equivariant/reduce steps are *proven but not yet assembled into a single cross-product-via-reduction
capstone* — that is "results present, arc not capped off" (a potential follow-up to add the capstone),
NOT dead code. Flagged for the maintainer; no action taken.

## Resolved

Nothing to remove or comment. The audit's one actionable item (the `_dot` orphans) was handled in the
sine/cosine task. If the maintainer considers a specific uncited result not worth keeping, annotate or
remove it case-by-case — but the default here is keep (they are the library's proven facts).
