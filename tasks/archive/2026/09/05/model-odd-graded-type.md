# Model the odd graded type `Odd_3` ({1,3}) in 𝒢₃, with a grade query + cast API

**Status:** COMPLETE 2026-09-05 — all steps done & verified (449 tests, ty clean, notebook executes);
commit history harvested below for the pre-squash summary; **ready to archive after the maintainer's
squash** (William Emerison Six <billsix@gmail.com>)
**Priority:** 3
**Difficulty:** 4

## BLUF

Register a new graded subtype **`Odd_3` = grades {1,3}** (the odd part of 𝒢₃) so the products that
currently widen to `G3` for lack of a `{1,3}` type instead return a proper named type — completing
𝒢₃'s even/odd naming (`Rotor` already names the even part {0,2}). Plus **(Option B, decided)** add a
**grade query + explicit cast API** so an `Odd_3` value can be narrowed to `Vector` or `Trivector`
when a grade actually vanishes — *without* making product return types value-dependent (the return
type stays operation-based; narrowing is an opt-in caller step). Ship it **for 𝒢₃ only**; the general
higher-dimension odd/mixed types are a **follow-up task created as the last step here**. Done =
`Odd_3` class generated, products resolve to it, query/cast API works, a percent-format notebook +
unit tests demonstrate query/cast/value-inspection, gacalc gate green.

## Context — read first

- **Concept:** `Odd_3` is a graded *subspace*, **not a subalgebra** — odd × odd = even, so
  `Odd_3 * Odd_3 → Rotor`, landing outside `Odd_3`. That's fine and normal (Vector/Bivector/Trivector
  aren't closed either). Full write-up: **`tasks/reference/graded-subspaces-vs-subalgebras.md`**.
- **How the generator types products:** `tasks/reference/generated-product-typing.md` — return type
  is resolved at generation time from the symbolic result's grade support ("smallest covering
  registered type, else widen to `G_n`"). Registering `Odd_3` makes `{1,3}` supports resolve to it
  automatically; **no product rules are hand-written.**
- **Design decision this task settles** (and updates in the docs): we keep return types
  **operation-based / value-independent** (rejected the value-dependent-runtime-narrowing option);
  the query/cast is the *opt-in* path to a precise type. See "Docs to update" below.

## The gap (confirmed)

Every product of two graded types lands in a registered type **except the odd part {1,3} in 𝒢₃**:

| product | grade support | current | after |
|---|---|---|---|
| 𝒢₂ `Vector * Bivector` | `{1}` | `Vector` ✓ | unchanged |
| 𝒢₂ `Rotor * Vector` | `{1}` | `Vector` ✓ | unchanged |
| **𝒢₃ `Vector * Bivector`** | **`{1,3}`** | **`G3`** ✗ | **`Odd_3`** |
| **𝒢₃ `Rotor * Vector`** | **`{1,3}`** | **`G3`** ✗ | **`Odd_3`** |
| **𝒢₃ `Rotor * Trivector`** | **`{1,3}`** | **`G3`** ✗ | **`Odd_3`** |

𝒢₁/𝒢₂ are **provably unaffected**: their odd part is just grade 1 (`Vector`), and the change is gated
`n >= 3` (nothing else hard-codes the graded set — everything reads `graded_specs(n)`).

## Decisions (made 2026-09-05)

1. **Name:** `Odd_3`. *(Note: existing graded classes are unqualified per-module — `Rotor`,
   `Trivector`, not `Rotor_3` — so `Odd` would match that convention. Confirm `Odd_3` vs `Odd` at
   implementation; the doc prose uses `Odd_3` regardless, mirroring how the docs write `Rotor_3`.)*
2. **Blades:** hard-filter to **grades {1,3}** (`len(b) in (1, 3)`), gated `if n >= 3`. NOT the
   general odd-subspace rule `len(b) % 2 == 1` — that equals {1,3} only through n=4 and picks up
   grade 5 at n≥5, making the name `Odd_3` dishonest. The general odd/mixed types for 𝒢₄⁺ are the
   follow-up (last step).
3. **Return typing = Option B:** products return the single named `Odd_3` (static, operation-based).
   No value-dependent runtime narrowing (Option A rejected). Precision is opt-in via query + cast.
4. **Scope:** 𝒢₃ only now; 𝒢₄/𝒢₅ (and the addition-born combinations like {0,1}, {1,2}, {2,3}) are a
   separate follow-up task, created as the final step below.

## The core change is one addition (anchors verified 2026-09-05)

Everything flows from **`graded_specs(n)`** — `tools/gen_specialized.py:651-667`. `Rotor` ({0,2}) is
declared there by an `if n >= 2:` block collecting even-grade blades; **mirror it** with an odd block:

```python
if n >= 3:  # odd part {1,3} of 𝒢₃ (mirror of Rotor = even part {0,2}); NOT a subalgebra
    odd_1_3 = tuple(b for b in blades if len(b) in (1, 3))
    specs.append(TypeSpec("Odd_3", odd_1_3, n, "graded"))
```

That one edit propagates automatically (subagent-verified 2026-09-05):

- **`TypeSpec`** — `gen_specialized.py:606-613` (`name, blades, dim, kind`); use `kind="graded"`.
- **`registry_for_dim(n, …)`** — `:674-676` splices `graded_specs(n)`, so `Odd_3` becomes a
  resolution candidate, a valid product-rhs operand, an emitted overload return, AND an emitted
  class — no other registry edit.
- **`resolve(support, n, …)`** — `:679-688` picks the smallest covering spec; a `{1,3}` support now
  finds `Odd_3` (4 blades) beating the full `G3` (8). (`Odd_3` and `Rotor` are both 4 blades but
  cover disjoint supports, so they never tie.)
- **`product_result`** — `:691-716` and **`unary_result`** — `:719-742` compute grade support
  symbolically and call `resolve`; so products/unaries auto-resolve to `Odd_3`.
- **Overloads/impls** — `product_overload_stubs` `:1518-1563`, `dispatch_method` `:1362-1506`,
  `alias_dispatch` `:1566-1596` all iterate `graded_specs(n)` → `Odd_3` gets its overload rows,
  match-arms, and a return type wherever a product resolves to `{1,3}`.
- **Class emission** — `main()` loop `:3442-3444` calls `generate_graded_type(spec, …)` (`:2618`)
  per spec → a full `Odd_3` dataclass (fields `coeff_e_1/e_2/e_3/e_123`, products, basis constants).

**Verify these don't need an `Odd_3` arm** (they're keyed on name prefix; `Odd_3` matches none, so it
correctly gets only the generic product/sum/unary machinery — no `exp`, coords, or sandwich):
`startswith("Bivector")` `:3034`, `"Rotor"` `:3064`, `"Vector"` `:3106`. Also auto-handled:
`generate_constants` resolves lone blades to `Vector`/`Trivector` (smaller than `Odd_3`), so no module
constant becomes `Odd_3`; `__all__` splices `graded_specs` names (`Odd_3` auto-exported);
`onto_types` for project/reject already filters to grade-pure specs (excludes `Odd_3`).

Consider narrowing `Vector.odd_part`/`Trivector.odd_part`/`Rotor.odd_part` once `Odd_3` exists
(`unary_result` will resolve a full 𝒢₃ odd part to `Odd_3`) — a small precision follow-on within this
task, not required for the core.

## The query + cast API (Option B — the opt-in narrowing)

Goal: from an `Odd_3` value, **query** which grade-pure type it actually is, inspect its
coefficients, and **cast** it to that concrete type (raising if a grade is nonzero). Build on
existing primitives (no new math):

- **Query (mostly already exists on `base.py`):** `grades()` (`:732`) → the present grades;
  `is_vector()` (`:674`, true iff support ⊆ {1}); `is_trivector()` (`:680`, support ⊆ {3});
  `coefficient(blade)` (`:425`) and `to_blade_dict()` (`:226`) to read values. So "is this `Odd_3`
  really a `Vector`?" is `odd.is_vector()`, and its value is `odd.coefficient(Vector.e_1)` etc.
- **Cast (new, small):** add explicit narrowing methods on `Odd_3` — `to_vector()` and
  `to_trivector()` — each checks the *other* grade is zero and rebuilds via the established pattern
  `type-narrow through from_blade_dict(... r_vector_part(r) ...)` used by `base.project` (`:854-869`)
  / `base.reject` (`:891-903`); raise `ValueError` (clear message) if the discarded grade is nonzero.
  Return the concrete `Vector` / `Trivector` type (typed precisely). *(Design sub-decision to settle
  in implementation: bespoke `to_vector`/`to_trivector` vs a single generic `narrow(TargetType)` that
  checks grade-support ⊆ target. Bespoke reads clearest for the 𝒢₃ pair; note it.)*

This keeps products value-independent (`Bivector * Vector : Odd_3`, always) while giving the caller a
sound, explicit way down to `Vector`/`Trivector` when the geometry makes a grade vanish.

## Building the test cases — the dual-of-wedge trick (maintainer's method)

To exercise the three `Bivector * Vector` outcomes, construct the vector's relationship to the plane
explicitly. For a plane `B = a ^ b` (a, b in 𝒢₃):

- **Perpendicular vector → pure `Trivector`:** `n = (a ^ b).dual()` (the cross-product direction) is
  ⊥ the plane, so `B * n` has only the grade-3 (wedge) part. Assert `(B * n).is_trivector()` and that
  `(B * n).to_vector()` **raises**, `(B * n).to_trivector()` succeeds.
- **In-plane vector → pure `Vector`:** any `v` in `span(a, b)` (e.g. `a`, or `a + b`) gives `B * v`
  with only the grade-1 (contraction) part. Assert `is_vector()`, `to_vector()` succeeds,
  `to_trivector()` raises.
- **General (parallel + perpendicular) → true `Odd_3`:** `v = a + n` (in-plane + perpendicular) gives
  both grades. Assert `grades() == [1, 3]`, both `to_*` raise, and the coefficient values match
  `B*a + B*n`.

Do this **symbolically** (sympy vectors) so it's exact, and also numerically. The `Gn` reference (a
separate code path) is the oracle for values.

## Work plan

1. **Explore/confirm** in a scratch script: symbolically evaluate the three products, confirm `{1,3}`
   support and eyeball the closed forms (sanity — the generator derives them).
2. **Register `Odd_3`** in `graded_specs(n)` (snippet above), gated `n >= 3`, blades `len(b) in (1,3)`.
3. **`make generate`** → inspect the regenerated `g3.py`: the `Odd_3` class, its products resolving in,
   `Vector * Bivector -> Odd_3`, `Odd_3 * Odd_3 -> Rotor`.
4. **Add the cast API** (`to_vector`/`to_trivector` on `Odd_3`) via the generator (a name-prefixed
   injection like the `Vector`/`Rotor` special cases, or a small generic helper). Query methods reuse
   base.
5. **Unit tests** (`tests/test_graded.py` + a focused new test, e.g. `tests/test_odd3.py`):
   - return types: `assert_type(Vector*Bivector, Odd_3)`, `Odd_3*Odd_3 → Rotor`, etc. (ty-gated).
   - the **query + cast**: the three dual-of-wedge cases above — `is_vector`/`is_trivector`/`grades`,
     `to_vector`/`to_trivector` success-and-raise, and **coefficient/value queries** on the narrowed
     results (`.x/.y/.z`, `coefficient(...)`).
   - add `Odd_3` to `test_conformance.py`'s `SPECIALIZED` map if it should run the shared suite.
   - `make test`, `make check-generated` (determinism), gate green.
6. **Notebook** — a **percent-format jupytext** notebook (e.g. `notebooks/displayodd3.py`, matching
   `displaygraded.py`) that: builds a plane, shows the three `Bivector * Vector` cases with LaTeX
   display, then **demonstrates querying** (`grades()`, `is_vector()`) and **casting**
   (`to_vector()`/`to_trivector()`, including a caught raise) and **inspecting the narrowed values**.
   This is the maintainer-facing "show it works" artifact.
7. **Docs** — see below; update the reference docs + README graded table + CLAUDE.md.
8. **Follow-up-task scaffold:** create `tasks/model-higher-odd-and-mixed-graded-types.md`
   (`proposed — needs go-ahead`) for 𝒢₄/𝒢₅ odd subspaces (general `len%2==1`) and the addition-born
   mixed types ({0,1} paravector, {1,2}, {2,3}, {0,3}, …), cross-linked here and to
   `generated-product-typing.md`. Note the g4/g5 "verify in full context" ty caveat from that doc.
9. **Investigate whether `Odd_3` simplifies the rotor-sandwich grade-preservation (maintainer's hunch
   — LAST step). — DONE 2026-09-05. Finding: hunch CONFIRMED.** The sandwich *implementation* is
   unchanged (the generated `Rotor.sandwich` was already `type(x)`-precise via whole-expression
   symbolic cancellation, proven in `2026/06/08/derived-sandwich-operation.md`; `base.sandwich` still
   rebuilds to `type(x)`; mvp uses `.sandwich()`, so no mvp behavior change). What `Odd_3` adds is
   exactly the *proof/typing*: the plain-product `R v R⁻¹` now types as the named `Odd_3` (support
   {1,3}) instead of widening to `G`, so grade-preservation is the **one-coefficient** statement
   `simplify((R * v * R.inverse()).coeff_e_123) == 0` — verified for a **general** symbolic rotor and
   captured in `tests/test_odd3.py::test_sandwich_grade_preservation_is_one_coefficient`. Docs
   refreshed: `design-decisions.md` (the sandwich note), `base.sandwich` docstring, and the
   `generated-product-typing.md` odd-gap note (flipped to CLOSED). Reference detail below is the
   original plan.

   `R v R⁻¹` now types through `Odd_3`: `R v` is even × odd = `Odd_3`, and `R v R⁻¹`
   is odd × even = `Odd_3` — so *showing the sandwich yields a `Vector`* reduces to showing the
   **single grade-3 coefficient `coeff_e_123` vanishes** for a unit rotor, instead of clearing the
   several non-grade-1 parts of the old `G3` form. Do:
   - Read the generated **`Rotor.sandwich`** (`gen_specialized.py:~3098`, a `dispatch_method` with
     `return_type=_OperandT` — grade-preserving by a *derived closed form*, no projection) and
     **`base.sandwich`**; judge whether the `Odd_3` intermediate makes the closed-form derivation or
     the grade-preservation argument cleaner / more legible.
   - Add a **one-line symbolic proof test** if it lands cleanly: over a symbolic **unit** rotor `R`
     and vector `v`, assert `(R * v * R.inverse()).coefficient(Trivector.e_123) == 0` — i.e.
     `R v R⁻¹` is in the vector subspace — much tighter than the pre-`Odd_3` argument. (`R v R⁻¹`
     types as `Odd_3`, so its only non-vector coefficient is `coeff_e_123`.)
   - Read **and update if relevant** the pertinent docs: `tasks/reference/generated-product-typing.md`
     (its `sandwich` / "odd-type gap" notes), `tasks/reference/unit-bivector-and-rotors.md`,
     `tasks/reference/design-decisions.md`, and the **archived sandwich/rotor tasks** — refresh any
     "`R v R⁻¹` widens to `G3`" framing to "`→ Odd_3`, grade-3 part provably zero" where the `Odd_3`
     lens genuinely simplifies the story.
   - Cross-check the **mvp rotation path** (`github.com/billsix/modelviewprojection`): the sandwich
     intermediate is now `Odd_3` not `G3` — expect no behavior change, just a tighter intermediate
     type; confirm mvp stays green.
   Investigation-and-document step: if it yields a cleaner grade-preservation proof/expression, capture
   it in the reference doc; if the projection/`sandwich` design is unchanged, record *that* too so it
   isn't re-investigated. (Note: this refines — does not contradict — the "Honest scope note" below:
   the runtime sandwich still hands back a pure `Vector`; what may get easier is the *proof/typing* of
   why.)

## Implementation log (chronological — harvested 2026-09-05 for the pre-squash summary)

The granular commits are labelled `updated`; this is the play-by-play they collapse into. In order:

1. **Decisions + docs first** (`152789f`, msg "make odd_3 …"). Wrote the subspace-vs-subalgebra
   reference doc (`graded-subspaces-vs-subalgebras.md`); rewrote this task with the decisions (Option
   B, name `Odd_3`, the gate, the blades); recorded the "type follows the operation" resolution in
   `CLAUDE.md` and the odd-gap note in `generated-product-typing.md`. **No code yet.**
2. **Core implementation** (`9d0a272`). Registered `Odd_3` via **one gated block in `graded_specs`** +
   the cast API injection. Two decisions made *while implementing*:
   - **Gated `if n == 3`, not `if n >= 3`.** A bare `n >= 3` with the literal name `"Odd_3"` would
     emit a class *named* `Odd_3` in `g4.py` at release (4-D's odd part is also {1,3}) — dishonest.
     `n == 3` keeps it g3-only and the name accurate; the general `n >= 3` / `len%2==1` case is the
     follow-up.
   - **Cast API as a name-prefixed injection** (`if spec.name == "Odd_3"`) generating
     `to_vector`/`to_trivector`, guarded by the inherited `is_vector()`/`is_trivector()` and raising a
     `ValueError` on the wrong grade. Chose **bespoke** `to_*` over a generic `narrow(T)` for clarity.
   - **Verified**: `Bivector*Vector → Odd_3` in all three geometric cases, `Odd_3*Odd_3 → Rotor`
     (odd·odd=even — the subspace-not-subalgebra fact), full-context ty clean. Updated the
     `test_graded` product-table entry (`Vector*Bivector`: `G3 → Odd_3`).
3. **Adhoc scripts promoted** (`6cdb5ea`): `inspect_odd3.py` (cast proof) + `verify.sh` (the
   full-context-ty harness — the *only* way to type-check the gitignored generated modules).
   (Also created the separate `refactor-conditionals-…` task here + in `242a70d` — not part of this
   task; harvested in its own doc.)
4. **Tests + doc-list** (`e8cac42`): `test_odd3.py` (the dual-of-wedge cases + cast + query);
   **discovered via a failing `assert_type`** that `Rotor.dual()` (the dual of the even {0,2}) is the
   odd {1,3} → now `Odd_3` (was `G`), fixed `test_operator_typing`; added `Odd_3` to the CLAUDE.md
   list + README table.
5. **Sandwich investigation** (`ddbcc4a`) — **finding, confirming the maintainer's hunch:** `Odd_3`
   does **not** change the sandwich *implementation* (already `type(x)`-precise since 2026-06-08 via
   whole-expression symbolic cancellation; `base.sandwich` still rebuilds; mvp uses `.sandwich()`, no
   behavior change). What it adds is the **proof**: the plain-product `R v R⁻¹` now types as `Odd_3`,
   so grade-preservation is the one-coefficient `simplify((R * v * R.inverse()).coeff_e_123) == 0`,
   verified for a **general** symbolic rotor. Refreshed the stale "widens to G" wording in
   `design-decisions.md` + the `base.sandwich` docstring; flipped the odd-gap note to **CLOSED**;
   added the two sandwich tests.
6. **Notebook + follow-up** (`3906a7e`): the `Odd_3` section in `displaygraded.py` (replaced the stale
   "widens to `g3.G`" cell; verified the whole notebook executes); the g4/g5 follow-up task
   (`model-higher-odd-and-mixed-graded-types.md`).

**Rejected along the way:** Option A (value-dependent runtime narrowing — kept operation-based typing);
the general `len%2==1` odd rule for the g3 impl (used hard {1,3} + `n==3` to keep the name honest —
deferred to the follow-up); a generic `narrow(TargetType)` cast (used bespoke `to_vector`/`to_trivector`).

**Final verification:** 449 tests pass, ty clean (tests + full-context generated modules), doc-regions
clean, the notebook executes.

## Docs to update (part of this task)

- **`tasks/reference/generated-product-typing.md`** — add a short section recording: the odd-type
  gap (line 136-140) is now filled by `Odd_3`; **decision: return typing stays operation-based /
  value-independent (Option A / value-dependent narrowing rejected)**, precision via opt-in
  query/cast.
- **`CLAUDE.md`** — the "Future directions › Graded subtypes" bullet says products' return type
  "follows the operation, never runtime float values." Affirm that principle (we did NOT go
  value-dependent), and note `Odd_3` closes the last 𝒢₃ product gap + the opt-in query/cast API.
  Add `Odd_3` to the graded-types list and the README "Graded subtypes" table.
- **`tasks/reference/graded-subspaces-vs-subalgebras.md`** — already written; cross-link from here.

## Honest scope note (acknowledged by maintainer 2026-09-05)

This is a **gacalc type-completeness / precision** change, valuable on its own merits (the maintainer
came to it independently). It is **not** an mvp fix: the rotor sandwich still projects to `type(x)`
(versor-ness isn't statically trackable), and mvp's `.scalar_part()`/`float()` coercions are
unrelated. What it buys: `Bivector*Vector` (etc.) return a named type instead of `G3`, the sandwich's
*intermediate* is named, and the new query/cast makes the odd→pure-grade narrowing first-class.

## Cost note

Generation runs the general `Gn` symbolic products; adding `Odd_3` adds its row/column of
derivations. 𝒢₃ regen is tens of seconds; this grows it modestly. Paid once at generate time; the
generated code stays fast.
