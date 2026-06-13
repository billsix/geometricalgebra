# Customizable blade symbols (G3 i/j/k), or a vector-calculus subclass (cross product, …)

**Status:** proposed — not started
**Created:** 2026-06-13

## Goal

Two intertwined ideas — settle which (or both):

1. **Customizable symbols.** Let blades display with custom names instead of the
   fixed `e_1`, `e₂₃`, … — so e.g. **G3 can show i / j / k**. (See open question on
   whether i/j/k label the basis *vectors* or the basis *bivectors*
   `e₂₃, e₃₁, e₁₂` à la quaternions.)
2. **Or a vector-calculus subclass.** Instead (or as well), a subclass — likely of
   the 3D representation — that defines familiar **vector-calculus** operations:
   the **cross product** first, possibly dot/scalar-triple-product, and maybe
   differential ops (grad/div/curl) if in scope.

These aren't mutually exclusive: custom symbols are about *display*; the subclass
is about *named operations*. The design step is deciding the split.

## Plan

- [ ] **Decide the shape.** Custom-symbol mechanism, vector-calc subclass, or both
      (symbols for presentation + a subclass for operations).
- [ ] **Customizable symbols.** Find where blade labels are produced —
      `blade_dict_latex` (`src/gacalc/base.py:46`), any `__repr__`/`__str__`, and
      the notebook/display code (`nbplotutils.py`, `notebooks/display*.py`). Design
      a symbol map (blade-tuple → display string), per representation or per render
      call. **Keep the internal blade-tuple representation unchanged** — it's the
      interchange format (see `[[blade-dict-tests-and-comments]]`); custom symbols
      are presentation only. Decide scope: LaTeX only, or `repr` too, or also
      constructors that *accept* i/j/k.
- [ ] **Nail the G3 "ijk" convention.** Are i/j/k the grade-1 basis vectors, or the
      grade-2 basis bivectors (`e₂₃, e₃₁, e₁₂`, matching the quaternion units)? This
      decides what the labels attach to.
- [ ] **Vector-calc subclass.** Design a 3D subclass exposing `cross(a, b)`. In GA
      the cross product is the dual of the wedge: `a × b = -I₃ (a∧b)` — reuse
      gacalc's existing `dual()` (`scalar.py:173`) and **verify the sign
      convention**. Consider dot (already `scalar_product`), the scalar triple
      product, and whether grad/div/curl are in scope.
- [ ] **Subclass vs. generated rep.** `g3` is code-generated (`tools/gen_specialized.py`).
      A hand-written subclass is likely cleaner than editing the generated file —
      weigh that; if extending the generated rep, change the source/template and
      regenerate (don't hand-edit `g3.py`).
- [ ] **Tests + docstrings.** Add tests (and valid `--doctest-modules` examples);
      use the house vocabulary (cross product framed as the dual of the wedge).

## Notes / decisions

- The blade tuple is gacalc's canonical interchange format — custom symbols must
  not change it, only how it's rendered (`[[blade-dict-tests-and-comments]]`).
- Cross product = dualized wedge; `dual()` already exists — mind the sign/orientation.
- Codegen + `--doctest-modules` constraints apply (see `CLAUDE.md`).
- If these ship, they want documenting — ties to `[[docstrings-for-sphinx]]`.

## Open questions

- **G3 i/j/k:** the basis vectors, or the basis bivectors (quaternion-style)?
- Custom symbols: display-only (LaTeX/`repr`), or also input (constructors taking
  i/j/k)? Global per representation, or per-render?
- Vector-calc subclass scope: cross product only, or the fuller set
  (dot / scalar triple product / grad / div / curl)?
- Implement as a hand-written subclass, or extend the generated `g3` rep?
