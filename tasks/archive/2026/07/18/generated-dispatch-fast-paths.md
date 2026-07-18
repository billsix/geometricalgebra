# Fast paths in the generated dispatch (measure with Code the Classics)

**Status:** complete
**Completed:** 2026-07-18 — core (#1 + #3 + #4) implemented + verified. All in the generator
(`tools/gen_specialized.py` + `tools/astbuild.py`); `gn.py`/`base.py` untouched;
generated `g*.py` gitignored (so `git diff` is `tools/`-only). Gates: **285 tests
pass, `check-generated` deterministic, ty + ruff clean, measured wins, zero
regressions.** Remaining: #2 (subsumed by #1), #5 (cast audit, minor), and the
sympy-leak (separate — `transforms.py`, opt-in). Code changes uncommitted (Bill's).
**Created:** 2026-07-09 (Bill: "log the fast path stuff as a task")

## Implemented (2026-07-18) — measured wins, no regressions

Confirmed against Bill's constraint (won't change functionality / won't degrade
perf). Micro-bench (ns/op, min-of-repeats), numeric coefficients:

| op | before | after | Δ |
| --- | ---: | ---: | --- |
| `Vector2.magnitude` | 863 | 145 | **+83%** (#4) |
| `Vector3.magnitude` | 1009 | 168 | **+83%** (#4) |
| `Vector2.normalize` | 1272 | 577 | +55% (via fast magnitude) |
| `V2+V2` / `Biv3+Biv3` / `V3+V3` | 457/576/505 | 200/231/245 | +56/60/52% (#1) |
| `V2*V2` / `V3*V3` | 592/714 | 392/528 | +34/26% (#1) |
| `V2 + float` | 656 | 412 | +37% (#3) |
| `V2 * float` (untouched path) | 320 | 321 | −0% (flat) |
| cross-type `V2*Biv2` / `V3*Biv3` | 635/1125 | 627/1127 | ~0% (within noise) |

- **#1 exact-type early-out** — `dispatch_method` prepends
  `if type(rhs) is <Self>: <closed form>` before the `match` (only for
  `cast is cast_self`, so the sandwich is untouched). Subtypes still fall to
  `case <Self>()`, so subclass preservation is unchanged. Verified cross-type does
  NOT regress (old-vs-new stash comparison).
- **#3 number-operand direct arithmetic** — the `number_case` arm now emits the
  Scalar-arm result reading bare `rhs` (via an empty-`attr` rename → bare name in
  `SymbolToAttr`), instead of `self.__add__(Scalar(...))` wrap + re-dispatch.
- **#4 closed-form `magnitude_squared`** — new generated override deriving
  `⟨~A A⟩` symbolically to direct field arithmetic (`e_1**2 + e_2**2`, `e_12**2`,
  …). base's `magnitude`/`normalize`/`__abs__` (untouched) call it via `self`, so
  they stop round-tripping through blade dicts. Numeric preservation intact
  (`(3e₁+4e₂).magnitude() == 5` exact for int input).
- **#2 folded into #1** — a full profiling-baked arm-frequency table was declined
  (clarity cost, arbitrary, marginal once #1 hoists the dominant same-type case).

## Motivation

The CTC games now use `gacalc.g2.Vector2` directly. The synthetic
busy-actor benchmark (2026-07-09, mvp container): **5.56 µs/actor-frame
direct gacalc vs 2.20 µs for the old two-float shim** — ~2.5× per-op
overhead, none of it math. Acceptable today (~6.7% of a 60 fps frame at
an unrealistic 200 busy actors), but if a game ever drags, the fix is
HERE — generator-level fast paths that every consumer inherits — never a
hand-written shim revival.

Where the time goes (per `a + b` on a graded type):

- the generated `__add__`/`__mul__`/product methods walk a `match rhs:`
  ladder (Scalar, Vector2, Bivector2, Rotor2, G2, numbers) — one
  isinstance-style class-pattern test per arm until the hit; the
  overwhelmingly common same-type case is not first.
- the number case of `__add__` wraps the scalar in an intermediate
  `Scalar(...)` object and re-dispatches instead of doing direct field
  arithmetic (scalar `__mul__` already does it right via `scaled_stmt`).
- `magnitude`/`magnitude_squared`/`normalize` are inherited
  `MultiVectorBase` methods that round-trip through
  `to_blade_dict()`/`from_blade_dict()` dict building instead of touching
  the named fields (compare: `sandwich` gets a generated closed form).
- `typing.cast(...)` / `cast_coef` are runtime identity *calls* on hot
  paths (cast is a real function call, ~50 ns each).

## Candidate fast paths (all in tools/gen_specialized.py — never hand-edit g*.py)

1. Emit an exact-type early-out before the match ladder:
   `if type(rhs) is Vector2: return type(self)(...)` — the same-type case
   skips the pattern machinery entirely.
2. Order the remaining match arms by measured frequency (see Metrics).
3. Number case of `__add__`/`__sub__`: direct field arithmetic (only the
   scalar field changes), no intermediate `Scalar` + re-dispatch.
4. Generated closed-form `magnitude` / `magnitude_squared` / `normalize`
   on the graded types (`sqrt(x*x + y*y)` on the named fields), keeping
   base.py's numeric-preservation rule (float in → float out; int routes
   through sympy for exactness; symbolic stays symbolic).
5. Audit `cast_coef`/`cast_self` emission on hot paths — where the
   checker allows, emit plain expressions instead of runtime `cast()`
   calls.

## Profiling findings (2026-07-18) — op-mix from 4 real workloads

Measured with an env-gated op-mix counter shim in the mvp container (method + raw
JSON: gacalc `tasks/profile-gacalc-op-mix-in-mvp.md`). **Widened past the original
2D-only scope — now includes 3D** (mvp demos/mvpViz exercise `Vector3`/`Bivector3`/
`Rotor3`). Counts include internal delegation (one `magnitude()` fans out to
`magnitude_squared`→`scalar_product`→`reverse`+`__mul__`).

| workload | dim | calls | dominant ops |
| --- | --- | ---: | --- |
| soccer (CtC) | 2D | 3.9 M | **magnitude chain ≈1.7 M** + same-type ×/+/−; scalar ×`float` 172k / `Float` 63k / `int` 7k |
| avenger (CtC) | 2D | 480 k | `__iter__` 175k + magnitude chain + same-type |
| kinetix (CtC) | 2D | 103 k | `__iter__` 93k (**90%**); rotor sympy-leak (`__mul__(One)`) |
| mvpViz perspective | 3D | 730 k | **`Rotor3.sandwich` 201k** + `Bivector3` add/mul ≈150k + `Vector3` same-type ≈328k |

Ranked levers (all behavior-preserving; conformance-guarded):
1. **Same-type exact early-out (candidate #1)** — same-type binary ops dominate
   *every* workload, 2D and 3D. Broadest win.
2. **Closed-form `magnitude`/`magnitude_squared`/`normalize` (#4)** — biggest 2D
   lever (soccer's magnitude chain ≈ 1.7 M of 3.9 M calls).
3. **Keep `Rotor3.sandwich` fast (already closed-form) + `Bivector3` fast paths** —
   the 3D levers the 2D CtC games never exercised.
4. **Number-case direct field arithmetic, float-first (#3)** — `float` ≫ `int` in
   practice (soccer 172k vs 7k).
5. **Fix the sympy `Float`/`One` leak** — numeric-preservation (perf ~6×/op + contract).

## Implementation approach (all in `tools/gen_specialized.py` — never hand-edit g*.py)

Verified against the *current* emitted code. #1–#3 are localized to one generator
function, **`dispatch_method`** (the `match rhs:` emitter); #4 is a new closed-form
emitter beside `unary_stmt`.

- **#2 order arms by frequency.** `dispatch_method` builds arms in a FIXED order:
  `for rhs_spec in [SCALAR, *graded_specs(n)]` → Scalar, Vector, Bivector, Rotor, then
  `_`. So `Vector2*Vector2` (hot) tests `Scalar()` first, then hits `Vector2()`. Fix:
  **sort that arm list by a frequency weight** (small table keyed by (self, method,
  rhs) from the op-mix) before emitting — same-type first, scalars next, rare
  cross-grade last. Arms are mutually exclusive by type → result-identical, just fewer
  failed pattern tests.
- **#1 exact-type early-out (pairs with #2).** In `dispatch_method`, prepend
  `if type(<param>) is <SelfType>: <same-type body>` before the `ast.Match`. The
  same-type body is exactly the `result_block_stmts(...)` already computed for
  `rhs_spec == self_spec` — hoist it. `type(x) is T` is one identity check vs the
  match's class-pattern isinstance, so `Vector2 ⊙ Vector2` skips the match entirely.
- **#3 direct field arithmetic for the number case.** Today the `number_case` arm
  emits `return self.<method>(Scalar(coeff_scalar=rhs))` — wraps + **re-dispatches**
  (confirmed in emitted `Vector2.__add__`). Fix: emit the **Scalar-arm result
  directly** with `rhs` substituted for `rhs.coeff_scalar` — reuse
  `product_result(self_spec, SCALAR, …)`'s `result_block_stmts` with a rename map
  binding the scalar field to the bare `rhs` name. No intermediate object, no second
  dispatch. (`__mul__`'s scalar case is ALREADY direct via `scaled_stmt`; this targets
  `__add__`/`__sub__`.)
- **#4 closed-form magnitude/normalize.** New emitter: for each graded self type,
  derive the closed form symbolically like the products do — evaluate
  `sym.reverse().scalar_product(sym)` on a symbolic instance → a scalar expr in the
  named fields (e.g. `e_1²+e_2²` for Vector2) → emit `magnitude_squared(self)` on the
  fields (cse + `expr_to_ast`). Then `magnitude(self)` = the **numeric-preserving**
  sqrt branch from base.py (float→`math.sqrt`, int→`sympy.sqrt`, symbolic→symbolic —
  do NOT reintroduce an unconditional `sympy.sqrt`; see `test_numeric_magnitude.py`),
  and `normalize(self)` = `type(self)(field/mag, …)`. These OVERRIDE the inherited
  base methods, touching named fields directly — no `to_blade_dict`/`from_blade_dict`
  round-trip. Conformance already compares graded magnitude to `Gn`.

## Metrics — REQUIRED: derive them from Code the Classics, in 2D (Bill)

**(Partly satisfied — see "Profiling findings" above; op-mix now collected for 4
workloads incl. 3D. Below is the original spec, kept for the before/after step.)**

Do NOT tune against guesses or a synthetic-only mix. The CTC games are
the real 2D consumer; use them to generate the numbers:

- **Op-mix profile**: instrument or statically count the games' vector
  operations (which dunders, which operand types — same-type add/sub,
  scalar mul, scalar_product, magnitude/normalize, rotor sandwich) across
  the 10 games' per-frame paths (soccer ball physics + AI, kinetix ball
  loop, avenger enemy swarm are the hot ones). The frequency table drives
  arm ordering (candidate 2) and says which fast paths matter at all.
- **Before/after benchmark**: the busy-actor mix from
  mvp `tasks/archive/2026/07/08/ctc-vector2-deferral.md` (2.20 µs shim /
  2.82 µs subclass / 5.56 µs direct baselines), rerun identically in the
  mvp container, PLUS a headless-loop measurement of at least one real
  game's update path if practical.
- Acceptance: meaningful reduction on the CTC 2D mix (target: within ~1.5×
  of the old float shim), `make test` (277+) green, `make check-generated`
  deterministic, format.sh clean, and mvp's ctc gates green against the
  result.

## Related (separate, pre-tag candidate — not this task)

`plane_rotation` numeric preservation: with a numeric theta the rotor
inherits sympy-exact coefficients from the int-coeff basis constants
(wedge -> normalize -> Rational), so every rotated vector comes back with
sympy Floats and downstream arithmetic goes ~6x slower (measured
2026-07-09: 3.71 vs 0.60 us per add). That's a correctness-of-contract
fix (base.py's numeric-preservation rule), wanted BEFORE the 0.0.8 tag;
kinetix's `_turn` and every mvp demo frame hit it.
