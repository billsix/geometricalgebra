# Decide what of the code generator to unit-test, and add those tests

**Status:** complete (2026-06-27) — determination made + tests added (`tests/test_generator.py`).
Ready to archive.
**Proposed:** 2026-06-27
**Completed:** 2026-06-27

## Question

The generator (`tools/gen_specialized.py` + `tools/astbuild.py`) had **no direct unit tests**. Its
*output* is well covered (conformance + graded suites exercise `G1/G2/G3` and the graded subtypes), and
determinism is guarded by `make check-generated`. But the generator's own **pure logic** — blade
naming, the type-resolution registry, term ordering — was only tested transitively. This task decides
what is worth testing directly and adds those tests.

## Determination — what to unit-test (and what not)

**Worth a direct unit test** (pure, deterministic logic with a clear input→output contract, and either
non-trivial or only *transitively* covered today):

1. **Blade ↔ name bijection** — `blade_label` / `blade_of_label` round-trip over all blades, plus the
   `() ↔ "scalar"` special case; and `field_name` (the `coeff_`-prefixed form). These underpin every
   emitted field and cse symbol; a regression would silently corrupt generation.
2. **`blades_for_dim` canonical order** — must be grade-then-index (`[(), (1,), (2,), (1,2)]`), because
   field order, `__iter__` order, and the docstrings all depend on it.
3. **`term_grade_key` ordering** — the key that makes generated sums read scalar→vector→bivector. Test
   that a grade-1 term sorts before a grade-2 term and that a product of an `a_`/`b_` pair keys on both.
4. **Type registry & resolution** — `registry_for_dim`, and `resolve` returning the **smallest covering
   registered type** else **widening to the full `G_n`** (`{()}→Scalar`, `{(1,),(2,)}→Vector2`,
   `{(),(1,2)}→Rotor2`, `{(1,),(1,2)}→G2`). This is the heart of "the type follows the operation."
5. **`product_result` / `unary_result` return-type resolution** — the gen-time determination of a
   product's result type from its symbolic grade support: `Vector2*Vector2→Rotor2`,
   `Vector2^Vector2→Bivector2`, `Bivector2*Bivector2→Scalar`, `Vector2.reverse→Vector2`,
   `Vector3.dual→Bivector3`. This is the single most important and subtle piece of generator logic.
6. **astbuild DSL invariants** — `parse_expr`/`module_source` round-trip; `SymbolToAttr` rewriting
   `a_e_1→self.e_1`; and `cast_coef`'s skip-vs-wrap policy (bare/negated field returned unchanged, a
   compound expression wrapped in `typing.cast(Coef, …)`). The cast policy is easy to break and feeds
   ty-cleanliness of the generated code.

**Deliberately NOT unit-tested** (already covered or low value/high churn):

- Generated-class *behaviour* (products, magnitudes, rotors) — owned by `test_conformance.py` /
  `test_graded.py`.
- Run-to-run determinism — owned by `make check-generated`.
- Exact emitted source **text** of whole methods — brittle golden-file testing; behaviour tests + the
  byte-identity habit cover it without freezing the formatting.
- ruff/ty cleanliness of generated output — owned by `format.sh` / CI.
- The thin ast-node builders (`nm`/`dot`/`call`/…) individually — exercised indirectly by the
  round-trip and by the generator running at all; only the non-trivial `cast_coef`/`SymbolToAttr` get
  their own tests.

## Done (2026-06-27)

Added **`tests/test_generator.py`** (imports `astbuild` + `gen_specialized` by putting `tools/` on
`sys.path`; importing the generator has no side effects — `main()` is `__main__`-guarded). Covers all
six categories above. All assertions were verified against the live generator before being written.

**Verified:** new tests pass; full suite green; `ruff` + `ty check tests` clean.

## Notes / cross-refs

- Builds on `tasks/archive/2026/06/07/gen-specialized-structure-refactor.md` (generator structure) and
  the just-completed `tasks/add-types-signatures-and-tools.md` (which made `tools/` ty-clean, so the
  test module's imports type-check).
- Per CLAUDE.md, the generated `g*.py` are gitignored build artifacts; these tests target the
  generator *logic*, not the emitted files.
