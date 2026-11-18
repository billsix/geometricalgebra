# Model the higher-dimension odd subspaces (𝒢₄/𝒢₅) and the addition-born mixed graded types

**Completed:** 2026-11-18 (William Emerison Six <billsix@gmail.com>; authorized batch
`ready-tasks-batch-2026-11-18`)
**Priority:** 7
**Difficulty:** 5
**Created:** 2026-09-05
**Follows:** `tasks/archive/2026/09/05/model-odd-graded-type.md` (the 𝒢₃ `Odd_3` precedent)

## Outcome

The odd-part type is now **`Odd`**, generated for every n ≥ 3 with that algebra's odd grades:
{1,3} in 𝒢₃ and 𝒢₄, and {1,3,5} in 𝒢₅. The odd products of the release-only g4/g5 therefore no longer
widen to `G`.

- **`tools/gen_specialized.py`:**
  - `graded_specs` registers `Odd` when `n >= 3`, with blades `len(b) % 2 == 1` (it was
    `if n == 3`, `Odd_3`).
  - `odd_extras` (formerly `odd3_extras`) generates one cast per odd grade from the type's own
    blades: `to_vector`, `to_trivector`, and in 𝒢₅ `to_fivevector` (through
    `is_homogeneous_of_grade_r`).
  - Every `Odd_3` in the custom 𝒢₃ docstrings became `Odd`. Those docs are applied only to g1–g3
    (`_CUSTOM_DOC_DIMS`), so g4/g5 get the generic ones.
- **The rename, everywhere outside the archive:** `src/gacalc/base.py` (two docstrings),
  `tests/test_odd3.py` → `tests/test_odd.py` (functions `test_odd_*`), `tests/test_graded.py`,
  `tests/test_operator_typing.py`, `notebooks/displaygraded.py`, `README.md` (the 𝒢₄/𝒢₅ rows gained
  `Odd`), `CLAUDE.md`, and seven reference docs.
- **`CHANGELOG.md` › Changed:** a breaking-rename entry (`g3.Odd_3` → `g3.Odd`), plus `Odd` in
  𝒢₄/𝒢₅.
- **New test:** `test_odd_holds_the_odd_grades_and_casts_to_each`, parametrized over whichever of
  g3/g4/g5 are generated, as `tests/test_conformance.py` does. It checks the field grades, that
  `e_3 * e_12` lands in `Odd`, and each cast.
- **modelviewprojection:** nothing to update. Its only `Odd_3` mentions are in its vendored copy of
  gacalc's source (`book/docs/_gacalc_src/`), which refreshes from gacalc.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-18)

1. Rename `Odd_3` to `Odd` (bare, like `Versor`); breaking, with a changelog entry.
2. Odd subspaces only. The addition-born mixed types ({0,1} the paravector, {0,3}, {1,2}, …) stay
   widening to `G`, and the paravector stays blocked on the maintainer's study of APS. The
   subspaces reference doc says so.

## Verification

- Generated g1–g5 with `GACALC_DIMS=1,2,3,4,5` (72 min, 𝒢₅ dominating). 𝒢₅'s `Odd` has
  `to_vector`, `to_trivector` and `to_fivevector`.
- Ran in the container against the existing image, with g4/g5 present:
  - full-context `ty check --no-respect-ignore-files src` over g1–g5: clean;
  - `pytest -m "not slow"`: 1901 passed, 2 skipped (g4/g5 conformance and the new `Odd` cases
    included);
  - `entrypoint/format.sh`: clean, no files changed;
  - the generator is deterministic (regenerated twice, `cmp` identical);
  - `tools/check_doc_regions.py`: OK.
