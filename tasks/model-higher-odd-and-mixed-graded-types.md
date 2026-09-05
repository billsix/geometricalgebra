# Model the higher-dimension odd subspaces (𝒢₄/𝒢₅) and the addition-born mixed graded types

**Status:** proposed — needs go-ahead (spun off 2026-09-05 from the 𝒢₃ `Odd_3` work)
**Priority:** 7
**Difficulty:** 5
**Part of / follows:** `tasks/archive/2026/09/05/model-odd-graded-type.md` (the 𝒢₃ `Odd_3` precedent — DONE 2026-09-05)

## BLUF

Extend the 𝒢₃ `Odd_3` idea outward: (a) name the **odd subspaces of 𝒢₄/𝒢₅** so their odd-producing
products stop widening to `G`, and (b) decide which **addition-born mixed grade-combinations**
({0,1} paravector, {1,2}, {2,3}, {0,3}, {2,4}, …) that currently widen are worth naming. This is
the deliberately-deferred "full completeness" half of the odd-type work; 𝒢₃'s `Odd_3` (the products
gap, and the one behind the rotor-sandwich) is already shipped. Scoped separately because it is
combinatorially larger, touches the release-only g4/g5, and one piece (paravectors) is blocked on
domain study.

## Context — read first

- **The 𝒢₃ precedent (mirror this):** `tasks/archive/2026/09/05/model-odd-graded-type.md` registered `Odd_3 = {1,3}` with
  **one gated block in `graded_specs(n)`** (`tools/gen_specialized.py`, currently `if n == 3:`,
  blades `len(b) in (1,3)`, name `"Odd_3"`) plus a name-prefixed `to_vector`/`to_trivector` cast
  injection in `generate_graded_type`. Everything else (resolve / product overloads / class emission)
  propagated automatically. That is the template.
- **Which grade-sets are subalgebras vs subspaces:** `tasks/reference/graded-subspaces-vs-subalgebras.md`
  (the odd part is a subspace, not a subalgebra; naming it is fine — Vector/Bivector/Trivector aren't
  closed either).
- **The g4/g5 ty caveat (critical):** the dev gate SKIPS the gitignored generated modules, and ty's
  checking is incomplete at small module scale — generating 𝒢₄ the first time surfaced **179 ty
  diagnostics that were latent (byte-identical) in 𝒢₃**. So any g4/g5 typing MUST be verified in
  **full context** (`ty check src/gacalc/g1.py … g5.py gn.py base.py functions.py transforms.py`
  together), not per-file, and not trusting a green g3-only run. See
  `tasks/reference/generated-product-typing.md` › "High-dimension ty findings" and
  `CLAUDE.md` › Dev workflow (the `ty check src/gacalc/g1.py … transforms.py` full-context line) to extend.
- **g4/g5 are release-only** (`GACALC_DIMS=1,2,3` in dev; 1,2,3,4,5 at `make dist`/`release`;
  ~5 min / ~87 min to generate) — see `tasks/reference/generated-algebra-generation-cost.md`. So this
  work is verified via the opt-in `make generate-all` / `make test-all-dims`, not the default gate.

## The odd subspaces (the tractable half)

The odd grades per dimension: **𝒢₃ = {1,3}**, **𝒢₄ = {1,3}** (4D has grades 0–4; odd = 1,3),
**𝒢₅ = {1,3,5}**. So generalizing the `graded_specs` block from `if n == 3:` to **`if n >= 3:` with
`len(b) % 2 == 1`** yields the right blade set at every dimension (it equals {1,3} through n=4, adds
grade 5 at n=5). Design decisions to settle:

1. **Naming + reconciling `Odd_3`.** The literal name `Odd_3` was chosen so it stayed honest under the
   `n == 3` gate. Generalizing needs a per-dimension name — either `f"Odd_{n}"` (so 𝒢₄ gets `Odd_4`,
   𝒢₅ `Odd_5`) or a bare per-module `Odd` (matching how `Rotor`/`Trivector` are unqualified per
   module). **Reconcile with the shipped `Odd_3`:** rename it to fit the scheme (a breaking change —
   changelog + mvp coordination) or keep `Odd_3` as a special case. Recommend deciding the scheme
   first, then either renaming `Odd_3 → Odd` (cleanest long-term) or documenting the exception.
2. **The cast API generalizes** — an odd value narrows to `Vector` (grade 1), `Trivector` (grade 3),
   and in 𝒢₅ also `FiveVector` (grade 5). The `to_<grade-pure>()` injection should be generated from
   the odd blade set, not hardcoded to `to_vector`/`to_trivector`.
3. **`Odd_4` note:** since 𝒢₄'s odd part is also exactly {1,3}, `Odd_4` and `Odd_3` have the *same*
   grade shape — a nice consistency check that the general rule is right.

## The addition-born mixed types (the larger, partly-blocked half)

Products only ever produce even-parity or odd-parity supports, so the *product* gaps are exactly the
odd subspaces above. But **addition** produces mixed-parity supports that still widen to `G`:
`{0,1}`, `{1,2}`, `{2,3}`, `{0,3}`, `{2,4}`, `{0,1,2}`, … There are many; name only the ones that earn
it:

- **`{0,1}` — the paravector** (scalar + vector; the Algebra-of-Physical-Space object). This is the
  notable one, but **BLOCKED**: `CLAUDE.md` › "Future directions › Paravectors" records that the
  author "does not yet know this area well enough to commit to a design … do not implement
  paravector-specific machinery" until APS is studied. So paravectors are their own gated sub-item —
  do not build until the maintainer greenlights after studying APS.
- **`{0,3}` in 𝒢₃** — IS a subalgebra (`≅ ℂ`, the central pseudoscalar; see the subspaces reference
  doc's scorecard) — a candidate worth naming on its own merits.
- **The rest** ({1,2}, {2,3}, {2,4}, …) — probably not worth naming (rarely hit; the `G` fallback is
  fine). Decide case by case; "leave at `G`" is a valid, common answer.

## Work plan

1. Decide the naming scheme (Q1) and whether to rename `Odd_3`.
2. Generalize the `graded_specs` odd block to `n >= 3` / `len(b) % 2 == 1`; generalize the cast
   injection to the odd blade set (Vector/Trivector/FiveVector).
3. `make generate-all` (or a scoped `GACALC_DIMS=1,2,3,4,5`), inspect g4/g5, and **full-context ty
   check** (per the caveat). Add g4/g5 odd types to `tests/test_graded.py`/`test_conformance.py` and
   run `make test-all-dims`.
4. Separately evaluate the addition-born mixed types; name `{0,3}` if wanted; **defer paravectors**
   (blocked on APS study).
5. Docs: extend the subspaces reference + README table + CLAUDE.md graded list; note the odd-subspace
   generalization.

## Open questions

1. **Naming scheme + `Odd_3` reconciliation** — `Odd_{n}` vs bare `Odd`; rename the shipped `Odd_3` or
   keep it as a special case? *(Recommend deciding the scheme, then renaming `Odd_3 → Odd` for
   long-term consistency, coordinated with mvp + a changelog entry.)*
2. **Scope** — odd subspaces only, or also `{0,3}` and/or the paravector? *(Recommend odd subspaces
   now; `{0,3}` optional; paravector deferred/blocked on APS.)*
