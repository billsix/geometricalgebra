# Precise project/reject/reflect typing onto ANY blade grade + ship G4/G5 by default

**Status:** Parts 1, 2 & 3 DONE + verified 2026-08-22. g4/g5 ship (release-only), have precise
`FourVector`/`FiveVector` graded types + precise onto-any-blade project/reject/reflect typing, and are
**fully ty-clean in full context** — the ty-imprecision spin-off (`generator-ty-clean-high-dim.md`)
is also DONE (179→0 across g1–g5, verified).
**Priority:** 4
**Difficulty:** 7
**Created:** 2026-08-22 (William Emerison Six <billsix@gmail.com>)

## Progress (2026-08-22)

- **Part 3 — release-only generation of g4/g5: DONE & verified.** `GACALC_DIMS` env var
  (default `1,2,3`) in `tools/gen_specialized.py` (`ALL_ALGEBRAS` declares g1–g5, `selected_dims()`
  filters); `make dist` generates the full set + bakes into the wheel; `entrypoint/shell.sh` stays
  default; `make generate-all` / `make test-all-dims` are the opt-in full-dim gate;
  `tests/test_conformance.py` imports g4/g5 conditionally and extends `CASES` over present modules;
  `setup.py` if-missing list stays `[g1,g2,g3]`. Docs updated (README "Generating the algebras",
  CLAUDE.md, reference doc). **Verified:** default generation → g1–g3 only, 370 tests pass, ruff+ty
  clean; `GACALC_DIMS=1,2,3,4` → g4 generates and **conformance incl. dim-4 passes (162 tests)**
  — proving the full-dim gate works and the `AXIS_NAMES` fix was the only n≥4 blocker. (g5's 87-min
  regen not re-run this session; it was already proven to generate end-to-end in the timing run.)
- **Part 1 — precise `onto: <BladeType>` overloads: DONE & verified.** `transform_factory_overrides`
  now emits one precise overload per grade-pure blade type, grade-capped per method (`project` → all
  grades; `reject`/`reflect` → ≤ Bivector, per Q3). Verified via `ty reveal_type`:
  `Vector.project(onto=<bivector>)(v)` and `onto=<trivector>` are now `Vector` (were
  `MultiVectorBase`) — the original teaching case. g1/g2/g3 fully ty/ruff/doc-region clean, 370 tests.

- **Part 2 — grade-4/5 graded types: types DONE + runtime-verified; ty-cleanliness SPUN OFF.**
  Added `grade_name(k)` (`Scalar`/…/`Trivector`/`FourVector`/…/`TenVector`, fallback `KVector{k}`);
  `graded_specs` now emits one grade-pure type per grade 1..n. Identical output for 𝒢₁–₃ (370 tests
  pass); 𝒢₄ generates `FourVector`, projects precisely onto it (`ty reveal_type` → `Vector`), and
  passes runtime conformance incl. dim-4 (162 tests). **But:** `ty check src` with g4 present reports
  **179 diagnostics, all in g4.py** (g1/g2/g3 stay 0). Root cause: **pre-existing** generator type
  imprecisions — `_coerce` typed `-> MultiVectorBase` (86 `invalid-assignment`), generated
  `__radd__` param narrower than base (5 `invalid-method-override`), `cast_coef` over-wrapping (40
  `redundant-cast` warnings), plus 40 `invalid-return-type` / 8 `invalid-overload`. The flagged lines
  are **byte-identical** to g3's (e.g. `left: G = _coerce(self, G)` at g3:1015 clean, g4:1881
  flagged), so this is ty analyzing the 3×-larger g4 module more thoroughly and exposing annotations
  that were always imprecise — **not** introduced by Parts 1/2 (which never touch those methods). It
  does **not** fail any gate (ty isn't run on g4/g5 — dev doesn't generate them, the full-dim gate
  runs pytest, release doesn't ty) and runtime is correct. Fixing it (generic `_coerce`, `__radd__`
  widening, `cast_coef` tightening) is a genuine improvement but a multi-item cleanup with slow
  (5-min g4 / 87-min g5) verify cycles → **spun off to `tasks/generator-ty-clean-high-dim.md`.**

## Goal

Two coupled asks, both in the **generated** types:

1. **Precise types when projecting/rejecting/reflecting a vector onto a blade of *any*
   grade** — not just onto another vector. For teaching, `Vector.project(onto=plane)(v)`
   should statically be a `Vector`, exactly like `Vector.project(onto=some_vector)(v)`
   already is.
2. **Add 𝒢₄ and 𝒢₅ to the default build** and make (1) hold there too (grade-4 and grade-5
   blades, up to each pseudoscalar).

## The problem, concretely (verified 2026-08-22)

Projecting/rejecting/reflecting a **vector onto a bivector already works at runtime** and
returns a precise `Vector` (`Vector.project(onto=e_12)(v)` → `Vector`). But the **static
type degrades** — proven with `ty reveal_type` on `g3`:

| call | revealed static type |
|------|----------------------|
| `Vector.project(onto=e_1)(v)`  (onto a **vector**)   | `Vector` ✓ |
| `Vector.project(onto=e_12)(v)` (onto a **bivector**) | `MultiVectorBase` ✗ |

**Why:** `transform_factory_overrides` (`tools/gen_specialized.py:1488`) emits precise
`@overload`s only for `<param>: Vector`, with everything else falling to a
`MultiVectorBase` catch-all. Its own docstring flags the deferral: *"higher-grade blades
stay `MultiVectorBase` -- the separate generalize task."* The overrides are also only
emitted on the `Vector` class (`if spec.name.startswith("Vector")`, `:2902`).

Projecting/rejecting/reflecting a **vector** is grade-preserving (the result is always a
vector), so `Vector.project(onto=<any blade>) -> ComposableFunction[Vector]` is
type-correct for every blade grade — the overloads just aren't emitted.

## Two blockers this exposes

### A. There are no graded types above grade 3

`graded_specs(n)` (`tools/gen_specialized.py:626`) generates only `Vector` (1), `Bivector`
(2), `Trivector` (3), and `Rotor` (even subalgebra). **There is no grade-4 or grade-5
type** — so in 𝒢₄/𝒢₅ a grade-4/5 blade has no precise type to name; it widens to the full
`G`. "Precise typing onto any blade" in 𝒢₄/𝒢₅ therefore *requires adding those graded
types first*. Naming is an open question (see below).

### B. reject/reflect onto grade ≥3 blades still raise at runtime

`reject`/`reflect` (`base.py`) handle only vector/bivector `away_from`/`across`; a trivector
falls to `case _: raise Exception("TODO ...")`, and a bivector-or-higher *value* hits
`assert value.is_vector()`. So a precise overload `reject(away_from=Trivector) ->
ComposableFunction[Vector]` would **promise a result that actually throws**. This task must
NOT emit precise overloads for a (method, blade-grade) pair whose runtime path raises — it
is gated on the runtime work in **`tasks/generalize-reject-reflect-higher-grade.md`**.

Grade coverage that is safe to type precisely **today**:
- **`project`** — onto every blade grade (vector, bivector, trivector, …): runtime works.
- **`reject` / `reflect`** — onto vector and bivector only; trivector+ waits on the
  generalize task.

## Plan

### Part 1 — precise overloads onto any (working) blade grade

- [ ] Rewrite `transform_factory_overrides` (`:1488`) to emit **one precise `@overload` per
      graded blade type present in the algebra** whose runtime path works for that method,
      each returning `wrapper[Vector]`, then the `MultiVectorBase | Sequence[...]` catch-all,
      then the delegating impl. It needs the list of graded blade specs (from
      `graded_specs(n)`), not just the `Vector` self-spec.
- [ ] Gate per method: `project` → all blade grades; `reject`/`reflect` → grades where the
      runtime path doesn't raise (currently ≤2). Drive this from a single predicate so it
      auto-widens when `generalize-reject-reflect-higher-grade.md` lands.
- [ ] Keep the runtime bodies unchanged (still `return super().<method>(...)`).
- [ ] `make check-regions` (the `Vector <method> method` doc-regions must stay balanced),
      `ty check` clean, and add a `reveal_type`-style typing test (or a `tests/` assertion)
      that `Vector.project(onto=<bivector>)(v)` is `Vector`, not `MultiVectorBase`.

### Part 2 — add grade-4 / grade-5 graded types

- [ ] Extend `graded_specs(n)` to add grade-4 (and grade-5) types for `n >= 4` / `n >= 5`,
      via a **`grade_name(k)` helper** so it scales instead of hand-listing each grade
      (decided per Q1 — the maintainer wants it to scale). See the naming table below.
- [ ] **Fix the known n≥4 generator bug FIRST** (see Timing below): `coordinate_property_defs`
      (`:769`, `AXIS_NAMES = ("x","y","z")` at `:766`) `IndexError`s on the grade-1 `Vector`
      of 𝒢₄ because `e_4` has no axis letter. Emit `x`/`y`/`z` only for axes within
      `len(AXIS_NAMES)`; `e_4`+ get no letter property (access via `coeff_e_4` /
      `.coefficient(...)`). Nothing generates at n≥4 until this is fixed.
- [ ] Then sweep for any *other* hidden grade-≤3 assumption (dual/product result resolution,
      the `i`/`plane_of_rotation` extractors, dispatch tables). Generate first, read the real
      g4/g5, then fix the generator — never hand-edit output.
- [ ] Wire the new types into the precise overloads from Part 1.

### Part 3 — ship higher dims without slowing dev (g4 default, g5 opt-in)

Full cost analysis lives in **`tasks/reference/generated-algebra-generation-cost.md`**
(g3 = 23.3 s, g4 = 4.9 min, **g5 = 87 min**; growth factor accelerating). The blocker for "by
default" is that `shell.sh`/`dist` regenerate **unconditionally on every invocation**.

**Chosen approach: (ii) release-only generation of the high dims** (decided 2026-08-22, Q4).
Parameterize the generated dim-set by build context via a `GACALC_DIMS` env var (default `1,2,3`):
`make shell` generates g1–g3 (dev never pays the g4/g5 cost at all); `make dist`/`make release` set
the full set so g4/g5 are generated **once at publish** and baked into the sdist/wheel. `setup.py`'s
if-missing `GENERATED` list stays `[g1,g2,g3]` so a git-checkout build doesn't accidentally pay the
~1.5 hr. Grounded in the real wiring: `entrypoint/shell.sh:7`, `Makefile` `dist:` (`:232`),
`setup.py` `BuildPyWithCodegen`. (Approach (i), only-if-missing caching, was rejected: it keeps g4/g5
locally tested but still pays the one-time cost in dev; release-only keeps dev at zero g4/g5 cost.)

Steps:

- [x] Add the `GACALC_DIMS` dim-set flag to `gen_specialized.py` (default `1,2,3`); `ALL_ALGEBRAS`
      declares `1..5`, `selected_dims()` filters into `ALGEBRAS`.
- [x] `make dist` invokes the generator with `GACALC_DIMS=$(ALL_DIMS)` (=`1,2,3,4,5`) so g4/g5 bake
      into the sdist/wheel; `entrypoint/shell.sh` leaves the default (`1,2,3`). (`release` depends on
      `dist`, so it inherits this.)
- [x] Kept `setup.py`'s if-missing `GENERATED = [g1,g2,g3]` (already correct).
- [x] **Opt-in full-dim gate:** `make generate-all` (full generation) and `make test-all-dims`
      (generate g1–g5 + run the suite). *A CI file doesn't exist in the repo yet — these targets are
      the gate; wiring them into CI is a follow-on if/when CI is added.*
- [x] `tests/test_conformance.py` imports g4/g5 conditionally and extends `CASES`/`SPECIALIZED` over
      whichever specialized modules are present (default: g1–g3; full-dim gate: +g4/g5).
- [ ] **Scope `make check-generated`** to a cheap dimension (or make high-dim determinism opt-in) —
      it regenerates *twice*, so g4/g5 there is brutal. *(Still default-dims only today, so it's not
      yet a problem; do this if `check-generated` is ever pointed at the full set.)*
- [x] Update docs: `README.md` ("Generating the algebras"), `CLAUDE.md` (Module-layout + Code
      generation + Where-generation-happens), reference doc. *(The graded-subtype list in Future
      directions is Part 2's concern — deferred with Part 2.)*

## Latent E501 in generated docstrings (surfaces only if g4/g5 leave the gitignore)

The generated `g*.py` carry over-long (E501) lines — auto-generated docstrings like the 102-char
`x`/`y`/`z` coordinate docstrings and the `"Spanning the basis blades: …"` line, which **grows with
dimension** (g4 Rotor ≈ 90 chars; g5 much longer). Today this is invisible: the files are gitignored,
`ruff check src` respects `.gitignore` and skips them (verified — `ruff check src` passes while
`ruff check src/gacalc/g3.py` reports 5 E501s), and the generator's `ruff_format` deliberately
suppresses the diagnostics.

It becomes a real issue **only if g4/g5 stop being gitignored where a linter sees them** — i.e. under
release-only Approach (ii) they're baked into the sdist/wheel, and a CI full-dim lint gate would run
ruff on them by explicit path. If g4/g5 ship, either wrap/shorten those generated docstrings in the
generator, or exempt E501 on generated files in the CI gate. Not a blocker for Parts 1–2; a
loose-end for Part 3.

## Notes / dependencies

- **Runtime already covers your teaching case** (vector onto a bivector) — this task is
  about the *static types* and about *extending to g4/g5*, not about making the plane-
  projection lesson run. That works now.
- **Depends on `tasks/generalize-reject-reflect-higher-grade.md`** for the reject/reflect
  grade-≥3 runtime paths; Part 1's per-method gate lets project go all the way now and
  reject/reflect catch up automatically when that task lands.
- Sibling: `tasks/precise-typing-remaining-methods.md` (other precise-typing work).

## Naming — the `grade_name(k)` scheme (decided 2026-08-22: `FourVector`/`FiveVector`…)

galgebra has **no named graded classes** (single `Mv`; generic *"r-vector" / "grade-r"*), so
there's nothing to copy from it. The maintainer chose a **number-word `…Vector` scheme that
scales trivially**: keep the three entrenched low-grade names, then spell grade k as the
English number word + `Vector`. Add a single helper `grade_name(k)` and drive `graded_specs`
(and everything that hard-codes `"Trivector"`) from it:

| grade k | name | | grade k | name |
|--------:|------|-|--------:|------|
| 0 | `Scalar`    | | 6  | `SixVector`   |
| 1 | `Vector`    | | 7  | `SevenVector` |
| 2 | `Bivector`  | | 8  | `EightVector` |
| 3 | `Trivector` | | 9  | `NineVector`  |
| 4 | `FourVector`| | 10 | `TenVector`   |
| 5 | `FiveVector`| |    | |

Scales to gacalc's whole supported range (basis constants stop at `e_10`, max grade 10) and,
unlike the Greek-prefix words (Tetra/Penta/Ennea…), needs no lookup table anyone has to
recall. Familiar `Vector`/`Bivector`/`Trivector` kept for grades 1–3.

> Minor caveat to note in the docstring: `FourVector` also names the *spacetime 4-vector* in
> physics; here it means a grade-4 blade in a Euclidean algebra. Worth one clarifying line so
> a physics reader isn't misled — not a reason to change the name.

## Timing (measured 2026-08-22)

**g4/g5 do not generate at all today** — there is a real grade/dimension bug that must be
fixed before they can even be timed:

The `AXIS_NAMES` bug (`coordinate_property_defs`, `:769`; `AXIS_NAMES = ("x","y","z")`, `:766`)
was fixed to enable measurement — skip the letter property for `e_4`+. Then, node-build time
(the dominant cost; ruff-format is negligible):

- **g3:** **23.3 s**  (2³=8 blades, 4³=64 term-pairs)
- **g4:** **292.5 s ≈ 4.9 min**  (2⁴=16 blades, 4⁴=256 term-pairs) — 12.6× g3
- **g5:** **5214.9 s ≈ 87 min (1 h 27 m)**  (2⁵=32 blades, 4⁵=1024 term-pairs) — 17.8× g4

The cost is superlinear and the growth factor *accelerates* (12.6× then 17.8× per +1 dim). Full
analysis: `tasks/reference/generated-algebra-generation-cost.md`.

### The real blocker for "by default" is the regen-on-every-invocation workflow

The generated `gN.py` are gitignored and **regenerated unconditionally on every `make shell`**
(`entrypoint/shell.sh`) and `make dist`, and **twice** for `make check-generated`. Today that's
~23 s (g1+g2+g3). Adding g4 makes **every `make shell` pay ~5 min** before a prompt; g5 makes it
**~87 min** — untenable for daily use, and `check-generated` doubles it (~3 hr for g5).

**So shipping g4/g5 by default must be paired with a generation-gating strategy** — either
incremental/only-if-missing, or release-only generation of the high dims. Both are laid out in
Part 3 (Approach (i)/(ii)); the choice is deferred to Open question 4.

## Open questions

1. ~~Naming~~ — **RESOLVED 2026-08-22: `FourVector`/`FiveVector`/… via a `grade_name(k)`
   helper** (table above).
2. ~~g5 by default?~~ — **RESOLVED 2026-08-22: g4 by default, g5 opt-in.** Measured
   g3 = 23.3 s, g4 = 4.9 min, **g5 = 87 min**. Full analysis:
   `tasks/reference/generated-algebra-generation-cost.md`.
3. ~~reject/reflect precise overloads onto trivector+~~ — **RESOLVED 2026-08-22: leave them
   widening to `MultiVectorBase` until the runtime generalize task
   (`generalize-reject-reflect-higher-grade.md`) lands.** `project` types precisely for all
   grades now; reject/reflect auto-widen when that task lands. This task is not blocked on it.
4. ~~Generation-gating strategy~~ — **RESOLVED 2026-08-22: Approach (ii), release-only.**
   Dev (`make shell`) generates g1–g3 only via a `GACALC_DIMS` dim-set flag (default `1,2,3`);
   `make dist`/`make release` set the full set so g4/g5 are generated once at publish and baked
   into the sdist/wheel. `setup.py`'s if-missing `GENERATED` list stays `[g1,g2,g3]`. **Requires a
   CI / opt-in full-dim gate** (`GACALC_DIMS=1,2,3,4,5 make test` + lint) so an n≥4 generator bug
   doesn't first surface at release — this is now a required part of the work, not optional.
