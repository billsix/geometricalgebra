# Precise project/reject/reflect typing onto ANY blade grade + ship G4/G5

**Created:** 2026-08-22 · **Completed:** 2026-08-22

Two coupled asks, both in the generated types:

1. **Precise types when projecting/rejecting/reflecting a vector onto a blade of any grade**, not just
   onto another vector: for teaching, `Vector.project(onto=plane)(v)` should statically be a `Vector`.
2. **Ship 𝒢₄ and 𝒢₅**, with (1) holding there too.

g4/g5 now ship (release-only) with precise `FourVector`/`FiveVector` graded types and precise
onto-any-blade typing, and they are fully ty-clean in full context thanks to the spin-off
`tasks/archive/2026/08/23/generator-ty-clean-high-dim.md` (179 → 0 diagnostics across g1–g5).

## The problem (verified 2026-08-22)

Projecting a vector onto a bivector already worked at runtime and returned a `Vector`, but the static
type degraded: `ty reveal_type` on g3 gave `Vector` for `Vector.project(onto=e_1)(v)` and
`MultiVectorBase` for `onto=e_12`. `transform_factory_overrides` (`tools/gen_specialized.py`) emitted
precise `@overload`s only for `<param>: Vector` (its docstring deferred higher grades), and only on the
`Vector` class. Since projecting/rejecting/reflecting a vector is grade-preserving, a
`ComposableFunction[Vector]` return is type-correct for every blade grade.

Two blockers:

- **No graded types above grade 3:** `graded_specs(n)` produced only `Vector`, `Bivector`,
  `Trivector` and `Rotor`, so a grade-4/5 blade widened to the full `G`.
- **reject/reflect onto grade ≥ 3 blades raised at runtime** (`case _: raise Exception("TODO ...")`,
  and `assert value.is_vector()` for a higher-grade value), so a precise overload there would promise a
  result that throws. That runtime work is `tasks/generalize-reject-reflect-higher-grade.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-22)

1. **Naming: a `grade_name(k)` helper**, keeping `Scalar`/`Vector`/`Bivector`/`Trivector` for grades
   0–3 and spelling grade k as the English number word + `Vector`: `FourVector`, `FiveVector`, …,
   `TenVector` (fallback `KVector{k}`). It scales to gacalc's whole range (basis constants stop at
   `e_10`), and unlike Greek prefixes (Tetra/Penta/Ennea) needs no table to recall. galgebra has no
   named graded classes (one `Mv`), so there was nothing to copy. A docstring line notes that
   `FourVector` here is a grade-4 Euclidean blade, not the physics spacetime 4-vector.
2. **Generation cost** (measured; `tasks/reference/generated-algebra-generation-cost.md`): g3 = 23.3 s,
   g4 = 292.5 s ≈ 4.9 min (12.6× g3), **g5 = 5214.9 s ≈ 87 min** (17.8× g4); superlinear, with an
   accelerating growth factor. Since `make shell` and `make dist` regenerated unconditionally (and
   `check-generated` twice), shipping g4/g5 had to be paired with a gating strategy. An interim answer
   ("g4 by default, g5 opt-in") was superseded by decision 4.
3. **reject/reflect onto trivector+ stay `MultiVectorBase`** until the runtime generalize task lands;
   `project` types precisely for all grades now, and a per-method predicate widens reject/reflect
   automatically later. This task was not blocked on it.
4. **Gating: release-only generation of the high dims** (Approach ii). Dev generates g1–g3 only; `make
   dist`/`make release` generate g1–g5 once at publish and bake them into the sdist/wheel. Rejected:
   Approach (i), only-if-missing caching, which keeps g4/g5 tested locally but still pays the one-time
   cost in dev. Release-only **requires an opt-in full-dim gate** so an n ≥ 4 generator bug doesn't
   first surface at release.

## What was done

- **Part 1, precise overloads.** `transform_factory_overrides` emits one precise overload per
  grade-pure blade type in the algebra, grade-capped per method (`project` → all grades;
  `reject`/`reflect` → ≤ Bivector), each returning `wrapper[Vector]`, then the catch-all and the
  delegating impl (runtime bodies unchanged). `ty reveal_type` confirmed `Vector.project(onto=<bivector>)`
  and `onto=<trivector>` give `Vector`, the original teaching case.
- **Part 2, grade-4/5 types.** Added `grade_name(k)`; `graded_specs` emits one grade-pure type per
  grade 1..n (identical output for 𝒢₁–₃). First fixed the n ≥ 4 generator bug that blocked generation
  entirely: `coordinate_property_defs` indexed `AXIS_NAMES = ("x","y","z")` and raised `IndexError` on
  𝒢₄'s `e_4`, so `x`/`y`/`z` are now emitted only for axes within `AXIS_NAMES` (`e_4`+ are read via
  `coeff_e_4` / `.coefficient(...)`). This turned out to be the only n ≥ 4 blocker. 𝒢₄ generated
  `FourVector`, projected precisely onto it, and passed runtime conformance including dim 4 (162
  tests). With g4 present, `ty check src` reported 179 pre-existing diagnostics in g4.py; their slow
  verify cycles (5-min g4 / 87-min g5) justified the spin-off named above.
- **Part 3, release-only generation.** A `GACALC_DIMS` env var (default `1,2,3`) in
  `tools/gen_specialized.py`: `ALL_ALGEBRAS` declares g1–g5 and `selected_dims()` filters them.
  `make dist` sets `GACALC_DIMS=$(ALL_DIMS)` (= `1,2,3,4,5`; `release` inherits it); `entrypoint/shell.sh`
  keeps the default; `setup.py`'s if-missing `GENERATED` list stays `[g1,g2,g3]` so a git-checkout build
  never pays ~1.5 h. `make generate-all` / `make test-all-dims` are the opt-in full-dim gate (there was
  no CI file yet). `tests/test_conformance.py` imports g4/g5 conditionally and extends
  `CASES`/`SPECIALIZED` over whichever modules exist. README ("Generating the algebras"), CLAUDE.md and
  the reference doc were updated.

## Left undone

- **`make check-generated` was not scoped** to a cheap dimension. It regenerates twice, so pointing it at
  g4/g5 would be brutal, but it still ran the default dims only, so the scoping was left until needed.
- **Latent E501 in generated docstrings:** the `x`/`y`/`z` coordinate docstrings (102 chars) and the
  "Spanning the basis blades: …" line, which grows with dimension. Invisible while the files are
  gitignored (`ruff check src` skips them; `ruff check src/gacalc/g3.py` reports 5 E501s, and the
  generator's `ruff_format` suppresses diagnostics). It matters only if a lint gate checks the baked
  g4/g5 by explicit path; then wrap the docstrings in the generator or exempt E501 for generated files.

## Verification

Default generation: g1–g3 only, 370 tests, ruff + ty clean, doc-regions balanced.
`GACALC_DIMS=1,2,3,4`: g4 generated and conformance including dim 4 passed (162 tests). g5 was not
re-run in this task (it had generated end-to-end in the timing run); the spin-off's final
`GACALC_DIMS=1,2,3,4,5` run passed ty and 198 full-dim conformance tests.

## Related

- `tasks/generalize-reject-reflect-higher-grade.md`: the reject/reflect grade ≥ 3 runtime work.
- `tasks/archive/2026/08/26/precise-typing-remaining-methods.md`: sibling precise-typing work.
