# Make the generated g4/g5 modules ty-clean (fix pre-existing type imprecisions surfaced at n≥4)

**Status:** DONE + verified 2026-08-22 — all 179 g4 ty diagnostics resolved by real fixes (not
suppressions). **Definitive `GACALC_DIMS=1,2,3,4,5` full-context ty run: "All checks passed!" (0
errors, 0 warnings) across g1–g5 + all hand-written modules; full-dim conformance 198 passed.**
Durable rules harvested to `tasks/reference/generated-product-typing.md`.
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-08-22 (William Emerison Six <billsix@gmail.com>)

## Context

Generating 𝒢₄ for the first time (via the release-only work + `grade_name`/`graded_specs`
generalization, `tasks/precise-blade-typing-and-g4-g5-default.md` Part 2) revealed that `ty check
src` reports **179 diagnostics, all in `g4.py`** — g1/g2/g3 stay fully clean. Runtime is correct
(dim-4 conformance passes, 162 tests), and **no gate fails** (ty is never run on g4/g5: dev doesn't
generate them, the full-dim gate runs pytest, release doesn't ty). So this is a code-*quality* issue
for the shipped high-dim modules, not a correctness or gating one.

**These are pre-existing generator imprecisions, not regressions.** The flagged lines are
byte-identical to g3's — e.g. `left: G = _coerce(self, G)` is clean at `g3.py:1015` but flagged at
`g4.py:1881`. The generated code pattern is dimension-independent; ty simply analyzes the 3×-larger
g4 module (529 KB vs 166 KB) more thoroughly and surfaces annotations that were always imprecise but
went unflagged at grade ≤3. (Confirmed 2026-08-22: the `precise-blade-typing` Part 1/2 edits never
touch `_coerce`/`__radd__`/`from_blade_dict`/`_geometric_product`.)

## The diagnostic categories (full-context `ty check src`, g4 present)

| count | rule | root pattern |
|------:|------|--------------|
| 86 | `invalid-assignment` | `left: G = _coerce(self, G)` — `_coerce` (`base.py:1190`) is typed `-> MultiVectorBase`, so assigning to a `: G` local is unsound to ty |
| 40 | `invalid-return-type` | `return G(...)` / graded constructors where the declared return (`Self` / resolved type) doesn't match to ty on the large module |
| 40 | `redundant-cast` (warning) | `typing.cast(Coef, d.get(...))` in `from_blade_dict` etc. — value already infers to `float | Expr`, so the cast is redundant |
| 8 | `invalid-overload` | the `project`/`reject`/`reflect` precise overloads (`ComposableFunction[Vector]` vs impl `[MultiVectorBase]`) — clean in g3, flagged in g4 |
| 5 | `invalid-method-override` | generated `__radd__(self, lhs: int \| float \| sympy.Expr)` is narrower than base `__radd__(self, lhs: MultiVectorBase \| Coef)` — a real Liskov narrowing |

## Candidate fixes (each a genuine improvement, verify on BOTH g3 and g4)

- [x] **Made `_coerce` generic** in `base.py`: `def _coerce[T: MultiVectorBase](x, cls: type[T]) -> T`
      (PEP 695) so `_coerce(self, G)` returns `G`. **Cleared all 86 `invalid-assignment` — g4 went
      179 → 93.** g1/g2/g3 stay clean (ty + 370 tests). (2026-08-22)
- [x] **Narrowed base `__radd__` param** `MultiVectorBase | Coef` → `Coef` (`base.py:279`) — it is
      only ever called with a bare number (a multivector left operand uses its own `__add__`), so
      `Coef` is both correct and matches the generated `__radd__`. **Cleared all 5
      `invalid-method-override` — g4 now 48 errors** (+ 40 non-failing warnings). g1/g2/g3 clean.
      (2026-08-22)
- [ ] **Tighten `cast_coef`** (`tools/astbuild.py`) so it doesn't wrap an expression ty already sees
      as `Coef` — would clear the 40 `redundant-cast` **warnings**. *Low priority: warnings do NOT
      fail `ty check` (exit 0 confirmed), so these don't block "ty-clean".*

## ROOT CAUSE of the residual 48 (investigated 2026-08-22 — they are REAL, and fixable)

Corrected understanding after reading the design + archive (`investigate-final-full-classes`,
`retype-even-odd-part-off-self`, `generated-product-typing`, `restore-ty-on-generated-sandwich`):
these are **not** a "ty is wrong on a big module" quirk. They are **genuine latent type
imprecisions** that ty happens to only surface at g4's scale (g3 passing is ty being *incomplete* at
smaller scale, NOT the code being sound). Both have clean, principled fixes.

### 40 `invalid-return-type` — `-> typing.Self` on the `@final` full class

The full class `G` is `@typing.final`, and `investigate-final-full-classes` (2026-07-23) made its
methods **construct `G(...)` concretely** but kept the return annotation `-> typing.Self`, reasoning
"Self ≡ G for a final class". ty does not fully collapse `Self` to `G` even under `@final`, so
`return G(...)` against `-> typing.Self` is flagged once the module is large enough for ty to check
it. **Fix:** emit `-> G` (the concrete class name) instead of `-> typing.Self` on the final full
class's own-type-returning methods. `G` being `@final` makes `-> G ≡ -> Self`, and it is a valid
narrowing override of base's `-> Self`. (Principled: it *finishes* the concrete-construction work
that task started — annotation now matches the concrete construction.)

### 8 `invalid-overload` — narrowing an INVARIANT generic (a real unsoundness)

`ComposableFunction`'s type param `V` is a plain **invariant** `TypeVar` — necessarily, since
`func: Callable[[V], V]` uses `V` as both input and output. The product overloads are sound because
they return **concrete multivector types** (`Rotor`, `Vector`) that are covariant subtypes of the
impl's `MultiVectorBase` return. But `project`/`reject`/`reflect` overloads return
`ComposableFunction[Vector]`, and `ComposableFunction[Vector]` is **not** a subtype of the impl's
`ComposableFunction[MultiVectorBase]` (invariance) — so the overload return is genuinely not
assignable to the impl return. **You cannot covariantly narrow an invariant generic.** This has been
latent since the `onto: Vector` overload landed (2026-08-03); ty only catches it at g4 scale. **Fix:**
broaden the generated impl's return annotation to `ComposableFunction[Any]` (the standard
"implementation signature is gradual" pattern) so each overload return is assignable to it. The impl
is never called directly (only the overloads are), so `Any` there is harmless; the overloads keep
their precise `ComposableFunction[Vector]`. (The narrowing to `[Vector]` stays optimistic-but-
runtime-correct — the func is grade-preserving — same spirit as the deliberate casts elsewhere.)

### Why NOT just suppress

Suppression would be wrong here **because these are real imprecisions, not false positives**: the
`Self`-vs-`G` annotation genuinely mismatches the concrete construction, and the invariant-generic
narrowing is genuinely unsound (ty is *correct* to flag it; g3 passing is luck of ty's incompleteness
at smaller scale). Suppressing would hide a real (if benign) type-lie that could mask a future real
one, and it would rot the moment ty's small-module checking catches up and starts flagging g1–g3 too.
The fixes above are small, principled, make the intent explicit, and improve g1–g3's soundness at the
same time — so there is no reason to suppress. (Suppression would only be justified if the fixes
proved to *contort* the generated output badly or ty were provably wrong — neither holds.)

## Plan for the residual — ALL FIXED (2026-08-22)

- [x] **`@final` types annotate the concrete class, not `typing.Self`** — `self_ann` in all three
      generators (`generate_scalar`/`generate_class`/`generate_graded_type`) now emits `-> Scalar` /
      `-> G` / `-> Vector` etc. `return G(...)` matches `-> G` exactly; the coerce branch's
      `cast(Self, …)` matches too (`Self <: G`); valid override of base's `-> Self`. **Cleared all 40
      `invalid-return-type`.**
- [x] **project/reject/reflect impl return → `wrapper[Any]`** (`transform_factory_overrides`) — the
      gradual impl type every invariant `ComposableFunction[Vector]`/`InvertibleFunction[Vector]`
      overload return is assignable to; impl never called directly. **Cleared all 8 `invalid-overload`.**
- [x] **Dropped the redundant `cast(Coef, d.get(b, 0))` in `from_blade_dict`** — `d: BladeCoef`, so
      `d.get(b, 0)` is already `Coef`. **Cleared all 40 `redundant-cast` warnings** (which DO fail
      `ty check` — it exits nonzero on them in this project, contrary to an earlier assumption).
- [ ] Final `GACALC_DIMS=1,2,3,4` confirmation (`ty check src` exit 0) — RUNNING; g1/g2/g3 already
      confirmed clean (ty + 370 tests) after every fix. One `GACALC_DIMS=1,2,3,4,5` confirmation still
      worth doing (g5, ~87 min) before closing, since g5 adds `FiveVector` + grade-5 products.

## Summary of the whole cleanup

| category | count | fix | kind |
|---|---:|---|---|
| `invalid-assignment` | 86 | generic `_coerce[T]` | real: `_coerce` was typed `-> MultiVectorBase` |
| `invalid-return-type` | 40 | `@final` types → concrete-name return annotation | real: `Self`≠concrete-construction under ty |
| `redundant-cast` | 40 | drop `cast(Coef, d.get(...))` in `from_blade_dict` | real: cast was always unnecessary |
| `invalid-overload` | 8 | impl return `wrapper[Any]` | real: can't covariantly narrow an invariant generic |
| `invalid-method-override` | 5 | base `__radd__` param → `Coef` | real: base param was semantically too broad |

**179 → 0.** Every fix is a genuine correctness/precision improvement that also makes g1–g3 more
sound (or is a no-op there); **none is a suppression.** All are generator/`base.py` changes; the
gitignored `g*.py` change on disk only.

### Two things the cleanup also exposed and fixed

- **`.gitignore` didn't cover g4/g5** — it listed `g1.py`/`g2.py`/`g3.py` explicitly, so generated
  g4/g5 were **untracked** (accidental-commit hazard) and `ruff`/`ty` checked them directly (which is
  actually why `ty check src` could see g4 at all). Replaced with the glob `/src/gacalc/g[0-9]*.py`
  (covers g1..g10+, but NOT the tracked hand-written `gn.py` — `'n' ∉ [0-9]`).
- **One stray `redundant-cast` per module** (the single-blade pseudoscalar's `magnitude_squared`,
  `cast(Coef, coeff**2)`): `Coef ** int` is already `Coef`. Extended `cast_coef` (`astbuild.py`) to
  skip a single `field ** constant` (multi-term sums still cast, since ty can't narrow the sympy sum).

### How this is verified (ty respects `.gitignore`)

ty (like ruff) **respects `.gitignore`**, so the dev gate `ty check src` **skips** all generated
`g*.py` — it only type-checks the hand-written modules. The generated modules' ty-cleanliness is
therefore verified by checking them **explicitly and together** (full context — a single-file
`ty check src/gacalc/g3.py` gives ~119 *isolation* false positives and is NOT a valid check):
`ty check src/gacalc/g1.py … g5.py gn.py base.py functions.py transforms.py nbplotutils.py`.
g1/g2/g3 confirmed **0 diagnostics** this way; the g4/g5 (`GACALC_DIMS=1,2,3,4,5`) run confirms the
rest. **Worth wiring this explicit full-context ty check into `make test-all-dims`** so g4/g5 ty
cleanliness can't silently regress (the dev gate can't see it).

## Verification (the slow part — plan around it)

- g1/g2/g3: fast (`make generate` ~23 s + `ty check src` + 370 tests).
- g4: **~5 min per regen** (`GACALC_DIMS=1,2,3,4 python tools/gen_specialized.py` then
  `ty check src`); g5: **~87 min**. So iterate the fixes against g4, and do ONE final g5 confirmation
  at the end rather than per-change. Target: `ty check src` clean with `GACALC_DIMS=1,2,3,4,5`.
- Consider wiring `ty check src` into the opt-in full-dim gate (`make test-all-dims`) once clean, so
  this can't regress silently.

## Related

- `tasks/precise-blade-typing-and-g4-g5-default.md` — the work that surfaced this (Part 2).
- `tasks/reference/generated-product-typing.md` — the generated-typing design.
- `tasks/reference/generated-algebra-generation-cost.md` — the g4/g5 regen costs.
