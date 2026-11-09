# Merge abstractBaseClass into master (regenerate generated code)

**Created:** 2026-06-06 · **Completed:** 2026-06-06

`master` and `abstractBaseClass` had diverged both ways from merge-base `c77907b`. `master` (6
commits ahead) held the math-notation docstrings, cleanups/hygiene, the "use match / modern python"
refactor, grade-sorted generated terms, and a prior merge of `origin/abstractBaseClass`.
`abstractBaseClass` (13 commits ahead) held the graded-subtypes work
(`tasks/archive/2026/06/06/graded-blade-subtypes.md`). Both had changed the generator and `base.py`,
and the generated files were huge (`g3.py` ≈ +2322 lines).

## Decisions

- **Don't merge the generated files; regenerate them.** `g1/g2/g3.py` and `scalar.py` are pure
  outputs of `tools/gen_specialized.py`, so only hand-written sources were merged and the outputs
  were regenerated from the merged generator, which removed the largest conflicts entirely.
- **A merge, not a rebase:** rebasing 13 commits would have replayed the same conflicts repeatedly.
- **Generator:** keep both sides — master's `emit_docstring`, `term_grade_key`/`blade_of_field` and
  `ruff_format`; the branch's registry/`resolve`, `generate_graded_type`, `generate_scalar`, the
  dispatch/result emitters, `unary_result`/`product_result`, narrowing `+`/`-`,
  `plane_of_rotation`. Master's grade ordering and math-notation docstrings were applied to the
  graded emission too, for consistency, and `main()` emits `scalar.py`, each full class plus its
  graded types, then runs `ruff_format`, so the manual format step went away. Where reconciliation
  was hard, master's structure was preferred and the graded functions grafted on.
- **`base.py`/`gn.py`:** keep master's correctness fixes (`reject`/`reflect` sequence handling, the
  `__rmul__` negation) and match modernizations, plus the branch's `basis_vector`, normalized
  `rotate(from, to)` and `rotor_from_vectors`. These do not flow through regeneration, so the hand
  merge had to preserve them.
- The follow-up drift guard for committed generated code became
  `tasks/archive/2026/06/06/regen-diff-ci-guard.md`.

## What was done

Master was merged into `abstractBaseClass` (`git merge master`) rather than on a separate
integration branch. There were two small conflicts, the `rotate` docstring and the generator's
`main()`, both resolved by combining the two sides. The generated files were regenerated from the
merged generator, everything was verified, and `abstractBaseClass` was then fast-forwarded into
`master`.

## Verification

141 tests pass; `ty` and `ruff` clean; the regen was deterministic (committed == freshly
generated); all notebooks (`displaymv`, `displayg2`, `displayg3`, `displaygraded`) ran headless.
