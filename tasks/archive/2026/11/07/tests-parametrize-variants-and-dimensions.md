# Fold near-duplicate tests into `pytest.mark.parametrize`, and write the technique into the Python standard

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>, who asked for it and for it to be done
in the same session). **Completed:** 2026-11-07.

## Outcome

The survey found test families worth folding, so they were folded, and the technique went into the
shared Python coding standard
(github.com/billsix/runClaudeInContainer `tasks/reference/python-coding-standard.md`, section "Tests: parametrize over the variants, don't copy
the test", mirrored byte-identically to github.com/billsix/runCrushInContainer's two copies). The
gacalc worked examples are in `tasks/reference/python-coding-standard-gacalc.md`. The standard went to
the shared doc, not the personal overlay in the dotfiles repo, because the rule is portable.

**Discovery.** A one-shot script, `discover.sh` (removed at archive; in git history with its `data/`
worklog), listed test-name families that collide
once a variant token (`_2d`, `_3d`, `_gn`, `_g2`, …) is stripped; it found 13. A `git grep` for loops over representations, dimensions and sample values inside
a test found 7 more.

**Folded:**
- `tests/test_frame.py`: the orthogonalization, Hestenes (reverse and inverse), prefix-blade and
  reciprocal-frame tests each became one test over a shared `FRAMES` list (symbolic 2D/3D, concrete 3D,
  graded g2/g3), so the graded and concrete frames now go through every check. The Hestenes
  reverse-form test also asserts the exact factor, `c_k = |A_{k-1}|² * w_k`. Prefix blades take
  `(vectors, expected)` pairs.
- `tests/test_frame_class.py`: forward, round-trip and inverse-equivalence tests run over module-scoped
  map fixtures picked by name; the graded round trip stacks two `parametrize` decorators. The 3D
  forward test gained the linearity check the 2D one had.
- `tests/test_dot_wedge_projection_split.py` (projection/rejection split), `tests/test_fixed_grade_dot_wedge.py`
  (four copies → two tests over four pairs; the reassembly test now also runs on 3D and g2/g3),
  `tests/test_rotor_from_vectors.py` (the Lagrange closed form; the sample-angle loop).
- In-test loops became `parametrize` in `tests/test_blade_dict.py` (three), `tests/test_measure.py`,
  `tests/test_transforms.py` (two), and the numeric Hestenes test in `tests/test_frame.py`.

**Kept apart**, with the reason recorded in the standard: the explicit-formula dot/wedge split tests,
the `typing.assert_type` tests, and the per-type sandwich tests (a parameter erases the static type each
one checks), and the inverse-equivalence test, which parametrizes the *pair* of methods.

**Result:** collected test cases 515 → 545 (excluding doctests), none lost (per-file counts were in the
adhoc `data/`); `entrypoint/format.sh` (ruff, ty, changelog) green; the full suite, doctests included,
passed (776 passed). One ty error came up and was
fixed: a list literal mixing `list[Gn]` and graded lists is not a `list[list[MultiVectorBase]]` (list
invariance), so the symbolic frame lists are annotated `list[MultiVectorBase]`; the standard notes it.
`tools/check_annotations.py` reports the same rows for the two frame test files as before the change.
