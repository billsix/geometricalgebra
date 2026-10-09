# Adopt Hestenes notation for variable names (Greek scalars, lowercase vectors, CAPITAL multivectors)

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-09-30 **Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Swept locals and private-helper bindings across `src/`, `tests/`, and the demo `notebooks/` so
variable names follow the Hestenes grade-class convention: **Greek** for a scalar (angles → `θ`/`φ`),
**lowercase Latin** for a vector, **CAPITAL Latin** for a bivector/trivector/pseudoscalar/versor/
general multivector. Public parameters were left (N803 on). The durable convention — rule table,
Greek-vs-Latin-fallback caveat, exempt names, tooling facts — now lives in
`tasks/reference/hestenes-variable-notation.md`; this doc is the lean work record. Both container
gates (`make format`, `make test` = 697 passed) green.

## What was done

A token-position codemod (`tasks/adhoc/hestenes-notation/apply_renames.py`) rewrote only NAME tokens,
scoped per enclosing function (src/tests) or per file (the shared-namespace notebooks), so string
labels (`sympy.symbols("theta")`) and comments were untouched. ~130 NAME tokens across 23 files:

- **Angles → Greek** (the headline): `theta`→`θ`, `phi`→`φ` at every in-scope local/private-param —
  `src/gacalc/base.py` (`exp`), `transforms.py` (`rotor_for`, a private closure param called
  positionally, so safe), `nbplotutils.py` (`generate_circle`), and the rotation/versor tests
  (`test_bivector_rotation`, `test_exp`, `test_plane_rotation`, `test_versor_extraction`,
  `test_rotor_from_vectors`, `test_matrix_template`), plus the `displayrotations` notebook. The
  `test_versor_extraction` `@parametrize("theta", …)` string was changed with its param.
- **Terse multivector locals → CAPITAL**: versors `r`→`R`/`r2`→`R2`/`r3`→`R3`, rotors `rhat`→`Rhat`,
  bivectors `b`→`B`/`b3`→`B3`/`biv`→`B`, trivectors `t`→`T`/`t3`→`T3`, the enumerated pseudoscalars
  `i2`→`I2`/`i3`→`I3`/`i1..i15`→`I1..I15`, the blade locals `a_prev`/`a_k`→`A_prev`/`A_k` in
  `frame.py` (the docstring already writes `A_{k-1}`/`A_k`), and the symbolic full multivectors in
  the notebooks (`a_full`→`A_full`, `g2_1`→`G2_1`, `c`→`C`, …). `displaygraded`'s `r`→`R0` avoided a
  collision with an existing `R`.

## Decisions made during the sweep (judgment calls, documented in the reference doc)

- **Greek is feasible and gate-clean.** Verified `θ`/`α`/`λ` pass `ruff check`, `ruff format`, and
  `ty check` with this repo's config (no non-ASCII-name rule selected); `ruff` treats a lowercase
  Greek letter as lowercase, so Greek satisfies N803 too.
- **Two tooling limits shaped the capital renames.** **N803** (on) forbids a CAPITAL *parameter*, so
  multivector params (e.g. `nbplotutils` private `mv`) stayed lowercase — only *locals* became
  capital. **E741** (in the selected `E` group) forbids a variable named exactly `I`/`l`/`O`, so a
  bare `I` is impossible.
- **The unit-imaginary `i` stays lowercase.** Bare `i`/`I` is both E741-blocked and the library's own
  idiom (the `.i()` API, the `i² = −1` prose), so single-letter `i` holding a unit bivector was left;
  only the enumerated `i2`/`i3`/`iN` pseudoscalars were capitalized (E741-safe, matching the `I₃`
  prose).
- **Descriptive multivector *words* were left** (`versor`, `rotor`, `plane`, `wedge`, `blade`,
  `conjugated`, `product`, `pseudoscalar`, `quarter`): the word already states the grade-class, the
  multivector analog of the scalar Latin-fallback. Only terse/abbreviated names were capitalized.
- **`tools/` was left out of scope.** Its GA-value locals are `bench.py`'s representation-tag
  benchmark names (debatable) and `gen_specialized.py`'s `_mv`/`_sym` oracle internals (deep
  generator internals, not reader-facing); neither affects a reader, so both were skipped.
- **Public parameters, module-level constants, cos/sin value letters `c`/`s`, and descriptive scalar
  names (`magnitude`, `angle`) were left** per Decision 1 and the Latin-fallback.

## Verification

- `ruff check .` clean; `ruff format` idempotent; `ty check src tests tools book/docs/notebooks`
  clean; `check_changelog.py` / `check_epix_keywords.py` clean.
- Codemod proven idempotent (second run renames 0 tokens).
- **Container gates** against the existing image (nested podman): `entrypoint/format.sh` all green;
  `pytest` **697 passed**.

## Open questions

None.
