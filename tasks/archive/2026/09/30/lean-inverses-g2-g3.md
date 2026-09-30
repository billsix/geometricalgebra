# Lean proofs — inverses in 𝒢₂ and 𝒢₃: is there a general formula, and what subset to prove?

**Part of:** `tasks/investigate-lean-proofs-for-ga.md` (the Lean-proofs umbrella)
**Related:** `tasks/archive/2026/09/30/lean-proofs-make-coordinate-free.md` (added `mul_vec_inverse_self`, the *vector* case).

**Status:** done (2026-09-29, William Emerison Six <billsix@gmail.com>) — investigation resolved; the
per-blade subset is proved in Lean; the general case is spun out to `tasks/lean-general-multivector-inverse.md`.
**Priority:** 3
**Difficulty:** 4

## Resolution (2026-09-29)

- **Is `Ã/|A|²` general? No.** It is a correct inverse only when `A Ã` is a scalar — blades and versors —
  not a mixed-grade multivector. Confirmed on paper (`A (Ã/|A|²) = A Ã / |A|²`, which is `1` iff `A Ã = |A|²·1`).
- **Is there a general formula? Yes**, in low dimensions (Hitzer–Sangwine 2017), built from the grade
  involutions — see `tasks/lean-general-multivector-inverse.md`, which now owns that work.
- **Subset proved in Lean (this session):** vector (`mul_vec_inverse_self`), versor
  (`versorFromVectors_mul_inverse`), **bivector (`mul_biv_inverse_self`)**, **trivector
  (`mul_triv_inverse_self`)** — all `A A⁻¹ = 1`, in `proofs/GacalcProofs/`. This covers every grade the
  library's `inverse` is validly used on, and suffices for the coordinate-free work.
- **Python:** `base.py:inverse`'s docstring was tightened to state the supported subset (blades/versors)
  instead of the vague "not sure," and `CLAUDE.md`'s known-issue note updated. A runtime guard is a
  separate open decision (perf on the versor hot path; symbolic-zero detection; published-API break) — see
  the reply thread / not yet added.

## BLUF

Investigate multivector inverses for 𝒢₂ and 𝒢₃ and reconcile them with the Python library, then decide
what to prove in Lean. The concrete question the maintainer posed: **is there a single general inverse
formula we can state and prove in Lean for an arbitrary multivector — and if not, say so**, and then pick
the subset of cases worth proving (vector, versor, bivector, trivector, …). "Done" for *this* task is the
written finding (general formula: yes/no, with the correct low-dimensional closed form if one exists) plus
a decided, cross-linked list of which inverse lemmas to add — **not** the lemmas themselves (those become
a follow-on task once the subset is chosen). Read-only until then.

## Context (cold-start)

**What "inverse" means here.** `A⁻¹` satisfies `A A⁻¹ = A⁻¹ A = 1`.

**The Python library uses ONE formula for everything** — `A⁻¹ = Ã / |A|²` (reverse over the squared
magnitude), `src/gacalc/base.py:1186` (`inverse`), where `|A|² = ⟨A Ã⟩` = `magnitude_squared`. It is
**self-flagged "not sure if I'm doing this correctly"** (docstring + `CLAUDE.md` "Assessment / known
issues" #2). That doubt is the crux of this task: `Ã / |A|²` is a correct inverse **only when `A Ã` is a
pure scalar** — true for a **blade** (grade-homogeneous simple element) and for a **versor** (a product of
vectors), but **false for a general mixed-grade multivector**, where `A Ã` has non-scalar parts and the
formula does not invert. So the honest statement is likely "the Python formula is the blade/versor inverse,
not the general one" — to be **verified**, not assumed (check what grades `inverse` is actually called on
in the games/tests; if it is only ever blades/versors, the formula is fine in practice and the docstring
should say so rather than stay vaguely uncertain).

**What Lean already has** (`proofs/GacalcProofs/`):
- `inverse` def, same `Ã/|A|²` formula, for both algebras: `Sandwich.lean:17` (G2), `Sandwich.lean:98` (G3)
  — `smul (1 / normSq a) (reverse a)`.
- **Proven `A A⁻¹ = 1` for exactly two cases so far:** the **vector** case `mul_vec_inverse_self`
  (`Projection.lean:89`, `a·a ≠ 0`) and the **versor** case `versorFromVectors_mul_inverse`
  (`Sandwich.lean:142`). Nothing proves it for a bivector, trivector, or a general element.
- Supporting leaves added recently: `reverse_vec`, `mul_vec_self` (`a a = |a|²·1`), `normSq_reverse_sandwich`.

**Is there a general closed form in low dimensions? (the lead to verify, NOT a settled fact.)** In
Clifford algebras up to dimension ~5 there are known closed-form general inverses built from the grade
involutions — reverse `Ã`, grade involution `Â`, Clifford conjugation `Ā` — chosen so the denominator
collapses to a scalar. The reference to check is **Hitzer & Sangwine, "Multivector and multivector matrix
inverses in real Clifford algebras" (2017)**. Sketches to confirm against that source before trusting:
- dim ≤ 2 (𝒢₂): `A⁻¹ = Ā / (A Ā)` with `A Ā` a scalar (Clifford conjugation), reportedly general.
- dim 3 (𝒢₃): a formula of the shape `A⁻¹ = (Â Ã Ā) / (A Â Ã Ā)` (three involutions) with a scalar
  denominator, reportedly general.
Neither is proven here; a durable Lean/reference claim needs the formula *derived or checked*, not copied.

## Investigation plan (read-only; produce a finding, then stop for the subset decision)

1. **Pin the domain of the current formula.** Prove/΅disprove on paper: `Ã/|A|²` inverts iff `A Ã` is a
   scalar; enumerate which 𝒢₂/𝒢₃ grades satisfy that (scalar, vector, bivector, trivector, versor, mixed).
2. **Reconcile with Python.** Where is `inverse` actually called (games, `pgzero_gl`, tests)? Only blades/
   versors, or ever mixed-grade? Decide whether the Python docstring's uncertainty is a real bug (mixed
   input silently wrong) or just under-documented scope. **If it is a latent bug, flag it** (own follow-on).
3. **Settle "is there a general formula?"** Verify the Hitzer–Sangwine low-dim closed forms for 𝒢₂ and 𝒢₃
   against the source; write the exact formula (with the involutions the codebase has: `reverse` exists;
   grade-involution / Clifford-conjugation may need adding). Report yes + formula, or no + why.
4. **Propose the subset to prove in Lean**, ranked, each as a `A A⁻¹ = 1` (and `A⁻¹ A = 1`) statement:
   vector (**done**), versor (**done**), bivector, trivector/pseudoscalar, even-versor, and — if step 3
   yields one — the general element. Note the pure-`ring` vs `field_simp` shape expected for each.

## Open questions

1. **Scope:** do you want a genuinely *general* multivector inverse proven in Lean, or is the per-case
   subset (vector ✓, versor ✓, + bivector, trivector) enough? (Rec: decide *after* step 3's finding — but
   my prior is the per-grade subset is the high-value part, since that is what the library actually inverts;
   a general formula is a stretch goal worth it mainly if step 2 finds real mixed-grade use.)
2. **On a "correct vs. matches-Python" split:** if the investigation confirms `Ã/|A|²` is wrong for
   mixed-grade inputs, should the Lean work prove the *correct* inverse (possibly diverging from Python)
   and file a Python-fix task, or stay scoped to the cases where Python's formula is already correct?
   (Rec: prove the correct one; file the Python reconciliation separately so the oracle and the proofs
   don't silently disagree.)

## Note

This task is investigation only. Per the request, once the finding lands we jointly pick the subset, and
the actual Lean lemmas go in a follow-on task (`proposed`), cross-linked here.
