# Model the odd graded type `Odd_3` ({1,3}) in 𝒢₃, with a grade query + cast API

**Created:** 2026-09-05 · **Completed:** 2026-09-05 (William Emerison Six <billsix@gmail.com>)

The work's step commits were squashed into `4e83680` ("make odd_3 because I want vector times rotor
to not return g"), merged in `fc32418`.

## The gap

Every product of two graded types landed in a registered type except the odd part {1,3} of 𝒢₃,
which widened to `G3`: 𝒢₃ `Vector * Bivector`, `Rotor * Vector` and `Rotor * Trivector` all have
support `{1,3}`. 𝒢₁/𝒢₂ were provably unaffected (their odd part is grade 1, `Vector`). `Odd_3` is a
graded **subspace, not a subalgebra** — odd × odd = even, so `Odd_3 * Odd_3 → Rotor` — which is
normal (Vector/Bivector/Trivector aren't closed either); full write-up in
`tasks/reference/graded-subspaces-vs-subalgebras.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-05)

1. **Name `Odd_3`**, mirroring how the docs write `Rotor_3`.
2. **Blades hard-filtered to grades {1,3}** (`len(b) in (1, 3)`), not the general odd rule
   `len(b) % 2 == 1`, which picks up grade 5 at n ≥ 5 and would make the name dishonest.
3. **Gated `if n == 3`, not `n >= 3`** (decided while implementing): 4-D's odd part is also {1,3}
   under the hard filter, so `n >= 3` would emit a class named `Odd_3` into the release-only `g4.py`.
4. **Return typing = Option B:** products return the single named `Odd_3`, static and
   operation-based. **Option A, value-dependent runtime narrowing, was rejected.** Precision is opt-in
   through a grade query + explicit cast.
5. **Bespoke `to_vector()` / `to_trivector()`** casts, chosen over a generic `narrow(TargetType)`
   for clarity on the 𝒢₃ pair.
6. **Scope 𝒢₃ only**; 𝒢₄/𝒢₅ odd subspaces and the addition-born mixed types ({0,1} paravector,
   {1,2}, {2,3}, {0,3}, …) went to the follow-up `tasks/model-higher-odd-and-mixed-graded-types.md`.

## What changed

- **One gated block in `graded_specs(n)`** (`tools/gen_specialized.py`), mirroring the `Rotor`
  even-part block: `TypeSpec("Odd_3", <blades of grade 1 or 3>, n, "graded")`. Everything else
  followed automatically: `registry_for_dim` splices `graded_specs`, so `Odd_3` became a resolution
  candidate, product operand, overload return and emitted class; `resolve` picks it (4 blades) over
  `G3` (8) for a `{1,3}` support (it never ties with `Rotor`, whose support is disjoint);
  `product_result`/`unary_result`, the overload stubs, `dispatch_method`, `alias_dispatch`,
  `__all__`, and class emission all iterate the specs. The name-prefixed special cases (`Bivector`,
  `Rotor`, `Vector`) correctly gave it nothing extra; no module constant resolved to `Odd_3`; and
  project/reject's `onto_types` already excluded non-grade-pure specs.
- **Cast API** injected for `spec.name == "Odd_3"`: `to_vector` / `to_trivector`, guarded by the
  inherited `is_vector()` / `is_trivector()`, raising `ValueError` on the wrong grade and returning
  the precise type. Querying reuses the base: `grades()`, `is_vector()`, `is_trivector()`,
  `coefficient(...)`.
- **Found via a failing `assert_type`:** `Rotor.dual()` (the dual of the even {0,2}) is odd {1,3}, so
  it became `Odd_3` (was `G`); `test_operator_typing` and the `test_graded` product table
  (`Vector * Bivector`: `G3 → Odd_3`) were updated.
- **Tests** in `tests/test_odd3.py`, using the maintainer's dual-of-wedge construction for a plane
  `B = a ^ b`, symbolically and numerically with `Gn` as the value oracle: a perpendicular
  `n = (a ^ b).dual()` gives a pure trivector `B * n`; an in-plane vector gives a pure vector; `a + n`
  gives a true `Odd_3` (`grades() == [1, 3]`, both casts raise, coefficients match `B*a + B*n`).
- **Notebook:** an `Odd_3` section in `notebooks/displaygraded.py` (replacing a stale "widens to
  `g3.G`" cell) showing the three cases, the query and the casts including a caught raise.
- **Docs:** `CLAUDE.md` (the "type follows the operation, never runtime values" principle affirmed;
  `Odd_3` added to the graded list), the README "Graded subtypes" table,
  `tasks/reference/generated-product-typing.md` (odd-gap note flipped to closed, Option A rejection
  recorded), and `tasks/reference/graded-subspaces-vs-subalgebras.md` (written for this task).
- Two ad-hoc scripts, `inspect_odd3.py` (the cast proof) and `verify.sh` (the full-context ty harness
  for the gitignored generated modules), were used during the work (removed at archive; in git
  history).

## Sandwich investigation (the maintainer's hunch — confirmed)

`Odd_3` did **not** change the sandwich implementation: the generated `Rotor.sandwich` was already
`type(x)`-precise via whole-expression symbolic cancellation
(`tasks/archive/2026/06/08/derived-sandwich-operation.md`), `base.sandwich` still rebuilds to
`type(x)`, and mvp uses `.sandwich()`, so github.com/billsix/modelviewprojection saw no behaviour
change. What it added is the proof: `R v` is even × odd = `Odd_3` and `R v R⁻¹` is odd × even =
`Odd_3`, so grade preservation became the one-coefficient statement
`simplify((R * v * R.inverse()).coeff_e_123) == 0`, verified for a general symbolic rotor in
`tests/test_odd3.py::test_sandwich_grade_preservation_is_one_coefficient`. The stale "widens to G"
wording in `tasks/reference/design-decisions.md` and the `base.sandwich` docstring was refreshed.

Scope note (acknowledged by the maintainer, 2026-09-05): this is a gacalc type-completeness change,
not an mvp fix — the rotor sandwich still projects to `type(x)` and mvp's `.scalar_part()`/`float()`
coercions are unrelated. Cost: `Odd_3` adds its row/column of symbolic derivations to 𝒢₃
generation (tens of seconds, grown modestly), paid only at generate time.

## Verification

449 tests pass; ty clean on tests and on the full-context generated modules; doc-regions clean;
the notebook executes. `make format`'s ruff step was not in the verify harness and failed afterwards;
that was fixed in `tasks/archive/2026/09/05/fix-make-format-ruff-errors.md`.
