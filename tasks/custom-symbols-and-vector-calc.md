# Customizable blade display symbols (G3 i/j/k) + a vector-calculus `cross`

**Status:** proposed — design settled with the maintainer 2026-08-31; needs go-ahead to implement
**Priority:** 5
**Difficulty:** 4 (revised down from 6 on 2026-08-31: the design questions are resolved and the
remaining work is localized — two render functions, one free function, tests)
**Created:** 2026-06-13 · **Design settled:** 2026-08-31
(William Emerison Six <billsix@gmail.com>)

## BLUF

Two small, independent features:

1. **Custom blade display symbols, set once per notebook.** A module-global symbol map
   (blade tuple → LaTeX string) consulted by the LaTeX renderers, so a setup cell like
   `set_blade_symbols({(1,): r"\mathbf{i}", (2,): r"\mathbf{j}", (3,): r"\mathbf{k}"})`
   makes every subsequent Jupyter display render e₁/e₂/e₃ as **i**/**j**/**k**. Display
   (LaTeX) only; the blade-tuple interchange format and `__repr__` are untouched.
2. **`cross(a, b)`** — one free function, `(a ∧ b).dual(3)`, sign verified by test.
   **No new class anywhere.**

Done means: the setup-cell workflow works in a notebook; `cross` exists with the sign
test green; suite + doctests pass; the book/notebook conventions are unaffected.

## Context (cold-start)

- **Read first:** `src/gacalc/base.py` — `blade_dict_latex` (~line 64, the LaTeX
  renderer, hardcodes `\mathbf{\vec{e}}_b`) and `_repr_latex_` (~line 1254, calls it);
  `src/gacalc/nbplotutils.py` — `_blade_latex` (~line 482, a *duplicate* of that
  hardcoding, used for plot labels); `src/gacalc/measure.py` — the free-function-module
  shape `cross` follows; `dual` in `base.py` (~line 719, `A·I⁻¹`).
- **Why no subclass (supersedes this doc's original framing):** the original idea was
  "a vector-calculus subclass of the 3D representation". That is now **impossible** —
  every generated value type became `@typing.final` (+ frozen/slots) on 2026-07-23,
  after this task was filed. The repo's established shape for representation-agnostic
  operations is a hand-written free-function module over `MultiVectorBase`
  (`frame.py`, `measure.py`); `cross` uses that shape.
- **Related:** `[[blade-dict-tests-and-comments]]` (the blade dict is the interchange
  format — symbols are presentation only), `[[docstrings-for-sphinx]]` (if these ship,
  they want documenting), `tasks/reference/design-decisions.md`.

## Decisions (settled 2026-08-31, William Emerison Six <billsix@gmail.com>)

1. **i/j/k label the basis VECTORS** (calc-3 î/ĵ/k̂) — not the basis bivectors.
   The quaternion-style bivector reading (and its e₃₁-sign wrinkle: canonical keys are
   sorted tuples, so e₃₁ = −e₁₃ can't be expressed by a rename-only map) is dropped
   from scope. Consequence: the symbol map is **rename-only, no per-blade signs**.
2. **Display-only, LaTeX-only.** `__repr__` stays as-is. The *input* side needs no
   library support at all: `i, j, k = e_1, e_2, e_3` at the top of a notebook already
   gives graded-`Vector` names (maintainer, 2026-08-31). No constructors accepting
   i/j/k.
3. **Mechanism — layered: pure parameter underneath, one module-global default on
   top.**
   - `blade_dict_latex(d, symbols: Mapping[Blade, str] | None = None)` — a pure
     function; a blade with no entry falls back to today's `\mathbf{\vec{e}}_b`
     rendering. Tests use this layer, so they stay deterministic.
   - A **single module-global map** (default empty = today's behaviour) consulted when
     the parameter is absent, set via `set_blade_symbols(...)` in a notebook setup
     cell. *Why a global is required, not a style choice:* Jupyter's rich display
     invokes `_repr_latex_()` with **no arguments** — per-call passing cannot affect
     plain cell-output rendering. Accepted costs: rendering is no longer a pure
     function of the value (that's the point, and it's kernel-scoped — each notebook
     kernel is its own process), and the map applies to every algebra at once
     (`(1,)` renders as **i** in 𝒢₂ too — acceptable for notebook use).
   - One global, **not** per-class state (per-representation registries on
     `G`/`Vector`/`Bivector`/… would multiply setup for no benefit).
4. **Thread the map through `nbplotutils._blade_latex` too**, deduplicating it with
   `blade_dict_latex`'s blade rendering while there (they currently hardcode the same
   string independently), so plot axis/legend labels honour the symbols.
5. **`cross(a, b) = (a ∧ b).dual(3)`** — a free function over `MultiVectorBase`
   (measure.py shape). Since `dual` is `A·I⁻¹` and `I₃⁻¹ = −I₃`, the existing `dual`
   is expected to give the standard right-handed sign — **verify by test**
   (`e₁ × e₂ = e₃`, plus a numeric comparison against `numpy.cross`). Guard to 3D:
   vector operands only, max basis index ≤ 3, clear `ValueError` (spirit of
   `measure._require_vectors`).
6. **The rest of the vector-calc wishlist is already covered or parked:**
   - dot — exists as `scalar_product` (document the correspondence, no synonym);
   - scalar triple product — exists: `measure.signed_volume(a, b, c)` **is**
     `a · (b × c)` (document the identity; add a test asserting it against `cross`);
   - grad/div/curl — **parked, out of scope**: they need multivector fields and a
     derivative operator, a different project.

7. **Placement (settled 2026-08-31, William Emerison Six <billsix@gmail.com>):**
   `cross` goes in a new small `src/gacalc/vectorcalc.py` (also the home for the
   dot ↔ `scalar_product` and triple-product ↔ `signed_volume` correspondence notes);
   a thin pass-through `MultiVectorBase.cross(other)` is added for discoverability
   (the `v.area(w)` precedent) — the generator-emitted narrowing overload
   (`Vector.cross(Vector) -> Vector`) was first parked as a separate follow-up,
   then approved and implemented the same day: see `[[generated-vector-cross]]`; the symbol
   registry + `set_blade_symbols` live in `base.py` next to `blade_dict_latex`
   (agent's call, delegated by the maintainer — `nbplotutils` already imports from
   `base`, and it keeps renderer and registry in one file).

## Plan

- [x] Add the `symbols` parameter to `blade_dict_latex`; add the module-global default
      map + `set_blade_symbols` in `base.py`, next to `blade_dict_latex`. Blade-tuple
      interchange unchanged. (Also factored the shared `blade_latex(blade, symbols)`
      renderer both callers use; `set_blade_symbols` validates canonical keys via
      `_require_canonical_blades`, whose value annotation was loosened to `object` —
      it only reads keys.)
- [x] Thread symbols through `nbplotutils._blade_latex`; dedupe the two renderers.
      (`_blade_latex` deleted; `nbplotutils` imports `base.blade_latex`. Two cosmetic
      rendering deltas from the unification: base's per-index subscript gained braces
      — `\vec{e}}_{1}`, renders identically — and plot blade labels lost their `\,`
      thin-space join.)
- [x] New `src/gacalc/vectorcalc.py`: `cross(a, b)` free function with the 3D/vector
      guard; docstring cites the duality (`a × b` as the dual of `a ∧ b`, house
      vocabulary). Thin pass-through `MultiVectorBase.cross(other)` on the base.
      (Dimension logic mirrors `measure.signed_content`: fixed types must have
      `DIMENSION == 3` — the generated `dual` raises on any other `n` — and `Gn`
      operands must use basis indices ≤ 3.)
- [x] Tests: sign (`e₁ × e₂ = e₃` — the right-hand convention CONFIRMED to fall out
      of the existing `dual`), numeric parity with `numpy.cross`, the triple-product
      identity vs `measure.signed_volume`, symbol-map rendering (via the pure layer),
      fallback rendering with an empty map, guard errors. Doctests valid under
      `--doctest-modules`. (`tests/test_vectorcalc.py`, `tests/test_blade_symbols.py`.)
- [x] Notebook demonstration: `notebooks/displayvectorcalc.py` — a setup cell doing
      both `set_blade_symbols(...)` and `i, j, k = e_1, e_2, e_3` (the alias is
      sanctioned for this notebook as the pairing with the display symbols; noted
      in-file), then calc-3-style examples using `cross`.
- [x] Docstrings note dot ↔ `scalar_product` and triple product ↔ `signed_volume`
      (the `vectorcalc` module docstring).

## Open questions

None — all design questions settled 2026-08-31 (see Decisions). The only remaining
gate is the maintainer's go-ahead to implement.

## Notes

- The blade tuple is gacalc's canonical interchange format — symbols must not change
  it, only how it's rendered (`[[blade-dict-tests-and-comments]]`).
- Codegen is untouched by this task; `--doctest-modules` constraints apply
  (see `CLAUDE.md`).
- If these ship, they want documenting — ties to `[[docstrings-for-sphinx]]`.
