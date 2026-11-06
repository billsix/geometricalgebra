# One shared "must be a vector (grade 1)" check, used everywhere gacalc hand-rolled one

**Done 2026-11-06.** Requested by William Emerison Six <billsix@gmail.com> twice: 2026-10-22 ("there is
some procedure somewhere that ensures the parameters are vectors … call the procedure instead, if it
makes sense") and 2026-11-04 (reuse an existing check instead of the nested `require_vector` in
`Frame.to_invertible_function`, and call it out in `CLAUDE.md`). The two task docs were merged on
2026-11-06; the earlier one is `tasks/archive/2026/11/06/consolidate-vector-grade-checks.md`.
Implemented on branch `refactor-frame-to-invertible-function`, after
`tasks/archive/2026/11/06/refactor-frame-to-invertible-function.md`.

## What was done

- **Added `MultiVectorBase.require_vector(value, context)` and `require_vectors(vectors, context)`**
  (static methods in `base.py`, beside `is_vector`). Both raise `ValueError` with a message naming the
  caller (`"<context> takes a vector (grade 1); got a non-vector: …"`); `require_vectors` also rejects
  an empty sequence. `CLAUDE.md` names them in "Conventions the agent must obey while writing code".
- **Real-`raise` sites routed through them:** `measure` (its private `_require_vectors` deleted),
  `frame.are_linearly_independent` (its empty case still returns `False` first),
  `Frame.to_invertible_function` (the nested `require_vector` deleted), `vectorcalc.cross`, and
  `implied_minimal_number_of_dimensions`.
- **`TypeError` → `ValueError`:** `bivector_from_vectors` (`MultiVectorBase` and `Gn` docstrings) and
  `transforms.plane_rotation`. Tests `tests/test_unit_bivector_i.py` and `tests/test_plane_rotation.py`
  updated. modelviewprojection was searched (`except`/`pytest.raises` on `TypeError`/`AssertionError`)
  and catches neither, so it needed no change.
- **Public-parameter `assert`s → the real check:** `is_orthogonal_to` and `is_parallel_to` (the vector
  check now runs before their zero-vector check), `versor_from_vectors` (and `rotor_from_vectors`, which
  delegates), and `transforms.projection_rotation`. Their "Raises: AssertionError" docstrings now say
  `ValueError`.
- **Left alone on purpose:** the `# TODO - can this be generalized?` asserts in `reject`/`reflect` and
  inside `projection_rotation`'s returned map (they mark a scope limit, not an input guard);
  `nbplotutils`' plotting-helper assert; `g2.rotate_90_degrees`' `TypeError` (an `isinstance` check that
  the argument is a `g2.Vector`, and generated code); `bivector_rotation`'s `TypeError` (a bivector
  check, outside this task). `tasks/reference/design-decisions.md`'s note that the quarter turn's
  `TypeError` "matches `plane_rotation`" was corrected.
- **`CHANGELOG.md` `[Unreleased]`:** an Added entry for the two checks and a BREAKING entry for the
  exception-type change.
- **Gates:** containerized `make test` (720 passed) and `make format` (ruff + ty, clean).

## Decisions

1. The shared check lives in `base.py`, the lowest module every caller already imports (William Emerison
   Six <billsix@gmail.com>, 2026-10-22).
2. Name it in `CLAUDE.md` (William Emerison Six <billsix@gmail.com>, 2026-11-04).
3. Form: static methods `require_vector(value, context)` + `require_vectors(vectors, context)` (the
   agent's recommendation, accepted 2026-11-06). The planned `require_nonempty` flag was dropped during
   implementation: its one motivating caller, `are_linearly_independent`, returns before the check on an
   empty sequence, so no caller needed it.
4. Every vector check raises `ValueError`, breaking callers that caught `TypeError` (William Emerison
   Six <billsix@gmail.com>, 2026-11-06: "I don't care if we break callers, only me, this project, and
   modelviewprojection use it").
5. Public-parameter asserts became real checks; the `# TODO` asserts, the notebook helper, and generated
   code were left alone (the agent's recommendation, accepted 2026-11-06).
6. The inventory in the merged doc attributed asserts to `inner_product`/`outer_product`; a re-grep
   found them in `is_orthogonal_to`/`is_parallel_to` instead, and those were converted.
