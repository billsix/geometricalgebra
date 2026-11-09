# Customizable blade display symbols (G3 i/j/k) + a vector-calculus `cross`

**Created:** 2026-06-13 · **Completed:** 2026-08-31 (design settled and implemented the same day;
shipped in 0.0.18, `tasks/archive/2026/08/31/release-0.0.18.md`)

Two small, independent features: (1) custom blade display symbols, set once per notebook, so a
setup cell like `set_blade_symbols({(1,): r"\mathbf{i}", (2,): r"\mathbf{j}", (3,): r"\mathbf{k}"})`
makes every later Jupyter display render e₁/e₂/e₃ as **i**/**j**/**k** (LaTeX display only; the
blade-tuple interchange format and `__repr__` untouched); (2) `cross(a, b) = (a ∧ b).dual(3)`. No new
class anywhere.

**Why no subclass:** the original framing was "a vector-calculus subclass of the 3D representation",
which became impossible once every generated value type was made `@typing.final` (+ frozen/slots) on
2026-07-23. The established shape for representation-agnostic operations is a hand-written
free-function module over `MultiVectorBase` (`frame.py`, `measure.py`), so `cross` followed it.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-31)

1. **i/j/k label the basis vectors** (calc-3 î/ĵ/k̂), not the basis bivectors. The quaternion-style
   bivector reading was dropped: canonical keys are sorted tuples, so e₃₁ = −e₁₃ can't be expressed
   by a rename-only map. So the symbol map is rename-only, with no per-blade signs.
2. **Display-only, LaTeX-only.** `__repr__` unchanged. Input needs no library support:
   `i, j, k = e_1, e_2, e_3` at the top of a notebook already gives graded-`Vector` names (the
   maintainer, 2026-08-31). No constructors accepting i/j/k.
3. **Layered mechanism: a pure parameter underneath, one module-global default on top.**
   `blade_dict_latex(d, symbols: Mapping[Blade, str] | None = None)` is pure (a blade with no entry
   falls back to `\mathbf{\vec{e}}_b`), and tests use it so they stay deterministic. A single
   module-global map (default empty) is consulted when the parameter is absent, set by
   `set_blade_symbols(...)`. The global is required, not a style choice: Jupyter calls
   `_repr_latex_()` with no arguments, so per-call passing cannot affect cell output. Accepted costs:
   rendering is no longer a pure function of the value (kernel-scoped), and the map applies to every
   algebra (`(1,)` renders as **i** in 𝒢₂ too). One global, not per-class registries (those would
   multiply setup for no benefit).
4. **Thread the map through `nbplotutils._blade_latex` too**, deduplicating it with
   `blade_dict_latex`, so plot labels honour the symbols.
5. **`cross(a, b) = (a ∧ b).dual(3)`**, a free function over `MultiVectorBase`, guarded to 3D vector
   operands with a clear `ValueError`; the sign was to be verified by test.
6. **The rest of the vector-calc wishlist was already covered or parked:** dot exists as
   `scalar_product` (correspondence documented, no synonym); the scalar triple product is
   `measure.signed_volume(a, b, c)` (identity documented and tested); grad/div/curl were parked as
   out of scope (they need multivector fields and a derivative operator).
7. **Placement:** `cross` in a new `src/gacalc/vectorcalc.py` (also home for the correspondence
   notes), plus a thin pass-through `MultiVectorBase.cross(other)` for discoverability (the
   `v.area(w)` precedent). The generator-emitted `Vector.cross(Vector) -> Vector` overload was first
   parked, then approved and built the same day in
   `tasks/archive/2026/08/31/generated-vector-cross.md`. The symbol registry and `set_blade_symbols`
   live in `base.py` next to `blade_dict_latex` (the agent's call, delegated by the maintainer:
   `nbplotutils` already imports from `base`).

## What changed

- `blade_dict_latex` gained the `symbols` parameter; the module-global map and `set_blade_symbols`
  were added in `base.py`, with a shared `blade_latex(blade, symbols)` renderer. `set_blade_symbols`
  validates canonical keys via `_require_canonical_blades`, whose value annotation was loosened to
  `object` (it reads only keys).
- `nbplotutils._blade_latex` was deleted; `nbplotutils` imports `base.blade_latex`. Two cosmetic
  deltas from the unification: the per-index subscript gained braces (`\vec{e}}_{1}`, renders
  identically), and plot blade labels lost their `\,` thin-space join.
- New `src/gacalc/vectorcalc.py`: `cross(a, b)` with the 3D/vector guard (dimension logic mirrors
  `measure.signed_content`: fixed types must have `DIMENSION == 3`, since the generated `dual` raises
  on any other `n`; `Gn` operands must use basis indices ≤ 3). Its module docstring cites the duality
  and the dot / triple-product correspondences. `MultiVectorBase.cross(other)` added.
- New notebook `notebooks/displayvectorcalc.py`: a setup cell doing both `set_blade_symbols(...)` and
  `i, j, k = e_1, e_2, e_3` (the alias is sanctioned for this notebook and noted in-file), then
  calc-3-style examples. Codegen was untouched by this task.

## Verification

`tests/test_vectorcalc.py` and `tests/test_blade_symbols.py`: the sign `e₁ × e₂ = e₃` (the
right-hand convention was confirmed to fall out of the existing `dual`), numeric parity with
`numpy.cross`, the triple-product identity vs `measure.signed_volume`, symbol rendering through the
pure layer, fallback with an empty map, and the guard errors; doctests valid under
`--doctest-modules`. Containerized gate, ruff/ty and pyright green. Related:
`tasks/archive/2026/07/29/blade-dict-tests-and-comments.md` (the blade dict is the interchange format;
symbols are presentation only) and `tasks/archive/2026/09/26/docstrings-for-sphinx.md`.
