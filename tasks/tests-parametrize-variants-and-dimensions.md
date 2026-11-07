# Fold near-duplicate tests into `pytest.mark.parametrize`, then write the technique into the Python standard

**Status:** proposed — the maintainer asked for it (William Emerison Six <billsix@gmail.com>,
2026-11-07); not started
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>)

## BLUF

Survey `tests/` for groups of test functions that differ only in a variant (an algorithm choice, a
representation `Gn`/`g2`/`g3`, a dimension 2D/3D, a frame), and fold each group into one parametrized
test using the techniques the 2026-11-07 frame work used. If the survey finds groups worth folding, fold
them; either way, record the techniques (and when not to use them) in the shared Python coding standard.
Done = the folds are made with the same tests passing (count of test *cases* unchanged or higher; no
assertion lost), `make format` green, and the standard updated in both sandbox repos.

## Context

The techniques, as used in `tests/test_frame_class.py` and `tests/test_frame.py` (2026-11-07):

1. **Parametrize over a named module-level list of the variants**, e.g.
   `INVERSE_METHODS: list[str] = ["reciprocal", "peel"]` and
   `@pytest.mark.parametrize("inverse_method", INVERSE_METHODS)`. A new variant is one line, and every
   test that loops over the list picks it up.
2. **Parametrize over data with readable `ids=`**, e.g. `frames_2d_and_3d` with `ids=["2d", "3d"]`, or
   `graded_frames` with `ids=["g2", "g3"]`, so a failure names the case.
3. **Share expensive objects through module-scoped fixtures, and parametrize over fixture names** with
   `request.getfixturevalue(name)` (`test_composed_round_trip_is_identity_3d_symbolic` over
   `["function_3d", "function_3d_peel"]`). A 3D symbolic frame costs about a minute, so building it once
   per module matters more than any other choice here.
4. **Keep a separate test where the assertion really differs** (the "inverse methods are equivalent"
   tests compare the two variants with each other, which a parametrized test cannot do).

Starting numbers (2026-11-07): 33 test files, 384 `def test_` functions, 45 `parametrize` uses. A rough
name scan (`_2d`/`_3d` pairs) finds a handful of families, for example in `tests/test_frame.py`:
`test_orthogonal_frame_{2d,3d}_symbolic`, `test_hestenes_parallel_to_rejection_{2d,3d}_…`,
`test_hestenes_inverse_equals_rejection_exactly_{2d,3d}_symbolic`, `test_prefix_blades_{2d,3d}_symbolic`;
and in `tests/test_frame_class.py`: `test_inverse_methods_are_equivalent_{2d,3d}_symbolic`,
`test_forward_sends_basis_to_frame_{2d,3d}`. Other files may repeat a test per representation
(`Gn`/`G`/graded) by hand; `tests/test_conformance.py` already parametrizes over `[Gn, G]` and is the
model for that axis.

**Where the standard goes** (decided while making this task): the technique is portable, not personal, so it
goes in the shared Python coding standard, canonical at github.com/billsix/runClaudeInContainer
`tasks/reference/python-coding-standard.md`, mirrored byte-identical to github.com/billsix/runCrushInContainer
(and the Crush baked copy the doc's header names). It does not go in the personal overlay in the dotfiles
repo, which holds maintainer-specific facts. A gacalc-specific worked example, if useful, goes in
`tasks/reference/python-coding-standard-gacalc.md`.

## Plan

1. Discover candidates with a shell search (save as `tasks/adhoc/tests-parametrize-variants-and-dimensions/discover.sh`,
   output to `data/`): test-name families differing by `_2d`/`_3d`, `_gn`/`_g2`/`_g3`, a method name, or
   a numeric/symbolic suffix; then read each family to confirm the bodies differ only in data.
2. Decide per family: fold, or keep apart with a reason. Do not fold when the bodies differ in what they
   assert, when the merged test would need `if`s on the parameter, or when one case is a slow symbolic
   test that should keep its own name.
3. Fold, one file per commit; compare the collected case count (`pytest --collect-only -q | tail -1`)
   before and after for each file.
4. Write the standard: a "Tests: parametrize over variants" subsection under (b) judgment calls, covering
   techniques 1–4 above and the do-not-fold cases from step 2. Canonical first, then mirror and check
   byte-identity.
5. Run `make format` and the full `make test`.

## Open questions

None.
