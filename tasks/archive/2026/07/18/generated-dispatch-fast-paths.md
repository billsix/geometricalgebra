# Fast paths in the generated dispatch (measure with Code the Classics)

**Created:** 2026-07-09 (the maintainer: "log the fast path stuff as a task") · **Completed:** 2026-07-18

Fast paths #1, #3 and #4 below were implemented and verified, all in the generator
(`tools/gen_specialized.py` + `tools/astbuild.py`); `gn.py`/`base.py` were untouched and the generated
`g*.py` are gitignored, so the diff was `tools/`-only. #2 was folded into #1; #5 (the cast audit) was
left undone as minor.

## Motivation

The CTC games had just switched to `gacalc.g2.Vector2` directly
(`tasks/archive/2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`). The synthetic busy-actor
benchmark (2026-07-09, mvp container) measured **5.56 µs/actor-frame direct gacalc vs 2.20 µs for the
old two-float shim**, ~2.5× per-op overhead, none of it math. The rule set then: if a game drags, the
fix is generator-level fast paths every consumer inherits, never a hand-written shim revival.

Where the time went, per `a + b` on a graded type: the generated methods walked a `match rhs:` ladder
(Scalar, Vector, Bivector, Rotor, G, numbers) with the common same-type case not first; the number
case of `__add__` wrapped the scalar in an intermediate `Scalar(...)` and re-dispatched (scalar
`__mul__` already did it right via `scaled_stmt`); `magnitude`/`magnitude_squared`/`normalize` were
inherited base methods round-tripping through `to_blade_dict()`/`from_blade_dict()`; and
`typing.cast(...)`/`cast_coef` are runtime identity calls (~50 ns each) on hot paths.

## Metrics (the maintainer's requirement: derive them from real workloads, not guesses)

The op-mix was measured with an env-gated counter shim in the mvp container
(`tasks/archive/2026/07/18/profile-gacalc-op-mix-in-mvp.md`), widened past the original 2D-only scope
to include 3D. Counts include internal delegation (one `magnitude()` fans out to
`magnitude_squared`→`scalar_product`→`reverse` + `__mul__`).

| workload | dim | calls | dominant ops |
| --- | --- | ---: | --- |
| soccer (CtC) | 2D | 3.9 M | **magnitude chain ≈1.7 M** + same-type ×/+/−; scalar × `float` 172k / `Float` 63k / `int` 7k |
| avenger (CtC) | 2D | 480 k | `__iter__` 175k + magnitude chain + same-type |
| kinetix (CtC) | 2D | 103 k | `__iter__` 93k (**90%**); rotor sympy leak (`__mul__(One)`) |
| mvpViz perspective | 3D | 730 k | **`Rotor3.sandwich` 201k** + `Bivector3` add/mul ≈150k + `Vector3` same-type ≈328k |

Same-type binary ops dominated every workload, 2D and 3D; the magnitude chain was the biggest 2D
lever; `float` far outnumbered `int` scalar operands.

## What was done

- **#1 exact-type early-out**: `dispatch_method` prepends `if type(rhs) is <Self>: <closed form>`
  before the `match` (only for `cast is cast_self`, so the sandwich is untouched), hoisting the
  same-type `result_block_stmts(...)`. Subtypes still fall to `case <Self>()`, so subclass preservation
  was unchanged; cross-type ops were verified not to regress (old-vs-new comparison).
- **#2 frequency-ordered match arms — folded into #1.** A profiling-baked arm-frequency table was
  declined: a clarity cost, arbitrary, and marginal once #1 hoists the dominant same-type case.
- **#3 number-operand direct arithmetic**: the `number_case` arm emits the Scalar-arm result reading
  the bare `rhs` (an empty-`attr` rename → bare name in `SymbolToAttr`) instead of
  `self.__add__(Scalar(...))` wrap + re-dispatch.
- **#4 closed-form `magnitude_squared`**: a new generated override derives `⟨~A A⟩` symbolically to
  direct field arithmetic (`e_1**2 + e_2**2`, `e_12**2`, …). base's `magnitude`/`normalize`/`__abs__`
  (untouched) call it via `self`, so they stopped round-tripping through blade dicts. Numeric
  preservation was kept (`(3e₁+4e₂).magnitude() == 5` exact for int input; no unconditional
  `sympy.sqrt`, guarded by `tests/test_numeric_magnitude.py`).
- **#5 `cast_coef`/`cast_self` audit on hot paths** was not done (minor).
- The sympy `Float`/`One` leak through `plane_rotation` was separate work in `transforms.py`
  (`tasks/archive/2026/07/09/plane-rotation-pretag-and-mvp-adoption.md`), not this task.

## Results (micro-bench, ns/op, min of repeats, numeric coefficients)

| op | before | after | Δ |
| --- | ---: | ---: | --- |
| `Vector2.magnitude` | 863 | 145 | **+83%** (#4) |
| `Vector3.magnitude` | 1009 | 168 | **+83%** (#4) |
| `Vector2.normalize` | 1272 | 577 | +55% (via fast magnitude) |
| `V2+V2` / `Biv3+Biv3` / `V3+V3` | 457/576/505 | 200/231/245 | +56/60/52% (#1) |
| `V2*V2` / `V3*V3` | 592/714 | 392/528 | +34/26% (#1) |
| `V2 + float` | 656 | 412 | +37% (#3) |
| `V2 * float` (untouched path) | 320 | 321 | flat |
| cross-type `V2*Biv2` / `V3*Biv3` | 635/1125 | 627/1127 | within noise |

This met the maintainer's constraint: no functional change and no performance regression.

## Verification

285 tests passed, `make check-generated` deterministic, ty + ruff clean.
