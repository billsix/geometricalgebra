# Prove `a ∧ b = 0 ⟺ a ∥ b` in Lean, so the library's claim is true

**Created:** 2026-11-08 · **Completed:** 2026-11-08
**Source:** `tasks/review/2026/11/08/repo-review.md` §7.1, §2.2
**Decision:** prove the converse rather than reword the claims. William Emerison Six
<billsix@gmail.com>, 2026-11-08, choosing option (a) over (b).

## What was wrong

Three places said Lean machine-checks `A ∧ B = 0 ⟺ A ∥ B`:

- the `MultiVectorBase.is_parallel_to` docstring (`src/gacalc/base.py`);
- `CLAUDE.md` › "Assessment / known issues" item 2;
- a `CHANGELOG.md` `[Unreleased]` › Fixed entry.

`proofs/GacalcProofs/Predicates3D.lean` proved only parallel ⟹ wedge zero (`wedge_parallel_smul`),
and said so in its header ("The converse … is not yet stated here"). There was nothing in 2D.

## What changed

- **`Predicates3D.lean` (namespace `GacalcProofs.G3`)** gains two theorems, in the object style
  (`IsVector` hypotheses, coordinates only in the body):
  - `parallel_of_wedge_eq_zero`: for vectors `a`, `b` with `a ≠ zero`, `wedge a b = zero` implies
    `∃ k, b = smul k a`. The proof reads the three bivector components of `a ∧ b`, splits on which
    component of `a` is nonzero, takes `k` as the ratio, and gets each remaining component from one
    of the equations.
  - `wedge_eq_zero_iff_parallel`: the `⟺`, from it and `wedge_parallel_smul`.

  The module header now states the equivalence.
- **`Predicates2D.lean` (namespace `GacalcProofs.G2`)** gains the 2D twins: `wedge_parallel_smul`,
  `parallel_of_wedge_eq_zero` and `wedge_eq_zero_iff_parallel`. G2 has no `zero` definition, so they
  use the literal `⟨0, 0, 0, 0⟩`, as `G2.wedge_isVector_isBivector_eq_zero` does. Its header now
  covers parallelism too.
- **The three claims** now say what is proved, naming `wedge_eq_zero_iff_parallel`: for vectors with
  `A ≠ 0`, `A ∧ B = 0 ⟺ B = k * A`.
- **`tasks/reference/lean-ga-proof-architecture.md`**: the `is_parallel_to` coverage row is now HAS,
  and the Predicates bullet names the new theorems.
- **`tasks/lean-frame-coverage.md`** (parked) notes that its planned k = 2 converse is done and can be
  reused.

## Forms

This adds the Lean form of a result the Python already implements and tests. No new symbolic-Python
cell or book page was added. The book has no parallelism page yet, and the Python `is_parallel_to`
tests are unchanged.

## Verification

- The proofs were first developed in scratch files with no warnings: each zero component is closed
  by `simp` with `mul_zero`, and each remaining component by an exact
  `field_simp`/`linear_combination` step, so no unused-tactic lints are added.
- `lake build`: success. The only warnings are the pre-existing ones tracked by
  `tasks/lean-proofs-remove-extras.md`.
- `bash proofs/check.sh`: "axioms gate: 1031 declarations rest only on propext, Classical.choice,
  Quot.sound" (1024 before), `[lean] OK`.
- The `is_parallel_to` doctest passes; `ruff`: clean.
