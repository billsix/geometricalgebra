# Per-type fixed-grade dot/wedge (via r_vector_part) and per-type sine/cosine, each proved equivalent to the general form

**Status:** DONE 2026-10-01 (William Emerison Six <billsix@gmail.com>) — all five phases landed; gates
green (`make format` ruff+ty, `make test` 671, `make lean` sorry-free). Remaining book voice pass spun
off to `tasks/levels-of-abstraction-book-voice-pass.md`.
**Priority:** 6 **Difficulty:** 7
**Created:** 2026-09-30 **Completed:** 2026-10-01

## BLUF

This added special-case, per-type *presentations* of the core operations as teaching artifacts beside
the canonical coordinate-free ones, each pinned equal by a check: an unsigned any-dimension `abs_sin`
(companion to the existing `cosine`), a signed 𝒢₂-only `sine`, a fixed-grade reading of dot/wedge
(`⟨ab⟩₀` / `⟨ab⟩₂` with the grade a literal), the Lean equivalences, and a pedagogy notebook showing
the coordinate → fixed-grade → coordinate-free chain. The coordinate-free form stayed the canonical
default; the lower rungs are teaching material (Decision 1), so the only new *API* was the two trig
methods. It realised the project principle that special-case formulas at every level of abstraction are
desirable for teaching provided a check proves them equal.

## The idea (maintainer, verbatim, 2026-09-30)

> For each type, make grade operation to get that grade. For each type, define wedge and dot, like how
> hestenes defines it, but call the grade, and bind the grade. Meaning that the grade calls will have
> fixed values. Also, Dedicated, per type definitions for sine and cosine. Make proofs that they are
> equivalent to the general formulas. … for the purposes of teaching, I'm perfectly happy with making
> special case formulas, including using coordinates entirely, all the way to coordinate free,
> indepedent of dimension … But for that, I would want checks to ensure that they are in fact the same
> … the default - coordinate free. … put in references to the more general cases, and prove that they
> are equivalent.

## What was delivered

**Phase 1 — `MultiVectorBase.abs_sin` (general, unsigned).** `|A ∧ B| / (|A| |B|)`, placed after
`cosine` in `base.py`, built from the same primitives so it preserves numeric input (float→float on the
generated classes, int/symbolic exact). Inherited by the generated classes via MRO — `cosine`/`abs_sin`
are not generator-specialized, so no generator change and `check-generated` stayed byte-identical. Tests
`test_multivector_abs_sin` + `test_abs_sin_cosine_pythagorean` (`cos²+abs_sin²==1`, numeric + symbolic).
The method was first named `sine` and renamed to `abs_sin` the same day once Decision 7 settled the
naming.

**Phase 2 — signed 𝒢₂ `sine` (per-type generated closed form).** The generator
(`tools/gen_specialized.py`, the `if n == 2:` vector-role block, beside `rotate_90_degrees`) emits
`g2.Vector.sine(other) -> Coef = (a∧b).coeff_e_12 · |a|⁻¹ · |b|⁻¹` — a signed scalar (Decision 8),
oriented (swapping the operands negates it), raising on a zero-length operand (Decision 6), 𝒢₂-only
(g1/g3 `Vector` have none). A dedicated `SINE_METHOD_DOC` carries doctests. Tests in
`tests/test_signed_sine.py` (signed value, swap-negates, parallel = 0, `abs(sine)==abs_sin`, symbolic
Lagrange, raises on zero, 𝒢₂-only). mvp `mathutils.py` `sine` was the behavioural reference.

**Phase 3 — fixed-grade dot/wedge demonstration + test.** `tests/test_fixed_grade_dot_wedge.py` pins,
for the grade-pure vector pair (Gn 2D/3D and generated g2/g3), that `dot = (a*b).r_vector_part(0)` and
`wedge = (a*b).r_vector_part(2)` — the grade a literal — equal the canonical
`inner_product`/`outer_product`, plus `ab = dot + wedge`. No new public method (Decision 1); the
`r_vector_part` grade projection already existed (Decision 2), so this was a demonstration that *uses*
it with a bound grade.

**Phase 4 — Lean equivalences.** `proofs/GacalcProofs/TrigEquiv.lean` (imported in the proofs root),
`make lean` green and sorry-free: `uvec_magnitude`; `cos_between_uvec` (`G2.cos_between` of two unit
vectors = `cos(β−α)`, via `uvec_dot`); a Lean `signed_sin_between` def (mirror of `g2.Vector.sine`)
with `signed_sin_between_uvec = sin(β−α)` (via `uvec_wedge`); `sin_between_eq_abs_signed_vec` (the
unsigned `G2.sin_between = |signed|` for any two vectors — the Lean mirror of `abs(sine)==abs_sin`); and
`sin_between_uvec = |sin(β−α)|`. The fixed-grade dot/wedge = graded-part needed no new theorem (already
`G2.vec_mul`/`mul_eq_dot_add_wedge`; cross-referenced in the file header).

**Phase 5 — pedagogy.** `book/docs/notebooks/levels-of-abstraction.py` (runs) +
`book/docs/levels-of-abstraction.rst` (in the `index.rst` toctree) show the coordinate → fixed-grade →
coordinate-free chain for dot/wedge (all equal), coordinate-free as dimension-independent (𝒢₂ and 𝒢₃),
and the trig family (`cosine`/`abs_sin`/signed `sine`, `cos²+sin²=1`). Prose/figures were left a draft
for the maintainer's voice pass — spun off to `tasks/levels-of-abstraction-book-voice-pass.md`.

**Other:** the new public API was recorded in `CHANGELOG.md` `[Unreleased]`. A pre-existing `ty` failure
in `tests/test_standardposition.py` surfaced during the gate runs and was fixed (recorded in
`tasks/reduce-to-standard-position.md`), and gacalc's `Dockerfile` got a uv cache mount — both unrelated
to the sine work.

## Decisions (maintainer; 1–5 on 2026-09-30, 6–8 on 2026-10-01)

1. **Keep the canonical names; the extra rungs are teaching material.** No competing public
   `dot`/`wedge`/`cosine` methods for the special cases — the coordinate-free forms kept those names and
   stayed the default. The fixed-grade and coordinate rungs became proved-equal notebook/test/Lean
   material. The only new *API* was the two trig names (Decision 7).
2. **"Per-type grade operation" meant the `r_vector_part`-style projection, which already existed** —
   not an integer grade-number accessor (an early misread). No new grade op was built.
3. **Dims/types:** vectors in g2+g3 first (agent's discretion, revisable).
4. **The general sine is unsigned** `|a∧b|/(|a||b|)` (named `abs_sin` per Decision 7).
5. **One task with a phase list**, not an umbrella.
6. **Zero-length guard: keep the raise (no NaN)** — consistent with the existing `cosine`; mvp's NaN
   guard is an mvp-side choice, not mirrored down.
7. **Trig naming follows mvp: `sine` = signed (𝒢₂), `abs_sin` = unsigned (any-dim).** The existing
   signed plotting helper `nbplotutils.sine` already matched. The two libraries are now consistent.
8. **`sine` returns a signed scalar `Coef`** (not a bivector) — the "just the numbers" trig family.
   The GA-native bivector alternative (`(a∧b)/(|a||b|) = sin θ·î`, making `cosine + sine` the rotor) was
   considered and not chosen; the bivector/rotor view stays available via the wedge and the product.

## Context that shaped it (as of 2026-09-30)

The codebase already had two rungs of dot/wedge — the coordinate-free Hestenes `inner_product`
(`base.py:735`) / `outer_product` (`:787`), and the generated per-type closed forms (proved == `Gn`
by the conformance suite via `product_result`/`resolve`/`dispatch_method`; see
`archive/2026/06/06/graded-blade-subtypes.md`, `archive/2026/07/22/add-left-right-contraction.md`). The
fixed-grade middle rung and the trig methods were what was missing. The Lean side already had
`Trig.cos_between`/`sin_between` and the angle-form `Rotation.uvec_dot`/`uvec_wedge` with no bridge
between them (the Phase-4 gap); `uvec_wedge` was already the signed 𝒢₂ sine, the ready-made target. The
"no abstract `⟨⟩_k` in Lean" decision (`archive/2026/09/30/lean-proofs-make-coordinate-free.md`) agreed
with binding the grade per type. The whole effort is an instance of the duplicate-definition theme
(`tasks/reference/reduction-to-standard-position.md`).

## Cross-references

- Follow-on: `tasks/levels-of-abstraction-book-voice-pass.md` (maintainer voice pass + figures).
- Prior art (adapted down, not imported): github.com/billsix/modelviewprojection
  `src/modelviewprojection/mathutils.py` (`cosine`/`sine`/`abs_sin`).
- Theme + mechanism: `tasks/reference/reduction-to-standard-position.md`,
  `tasks/reference/contraction-and-dot-definitions.md`, `tasks/reference/generated-product-typing.md`,
  `tasks/reference/lean-ga-proof-architecture.md`.
- Deliverables: `proofs/GacalcProofs/TrigEquiv.lean`; `tests/test_signed_sine.py`,
  `tests/test_fixed_grade_dot_wedge.py`; `book/docs/notebooks/levels-of-abstraction.py`.
