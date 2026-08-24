# Generated `__eq__` — same-type field comparison instead of always via blade dict

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-08-24 (William Emerison Six <billsix@gmail.com>)

## Context

Every generated value type (the full `G` and the graded subtypes) shares one `__eq__`,
emitted by `eq_method()` in `tools/gen_specialized.py:872`. It **always** round-trips both
operands through the blade-dict interchange, unions the key sets, and does a per-blade
`sympy.simplify(sympify(l) - sympify(r)) == 0`:

```python
def __eq__(self, other) -> bool:
    if not isinstance(other, MultiVectorBase):
        return NotImplemented
    left: BladeCoef = self.to_blade_dict()
    right: BladeCoef = other.to_blade_dict()
    return all(
        sympy.simplify(sympify(left.get(blade, 0)) - sympify(right.get(blade, 0))) == 0
        for blade in set(left.keys()) | set(right.keys())
    )
```

For the common case — comparing two values of the **same** specialized type
(`Vector == Vector`, `G == G`) — building two dicts, allocating two key-sets, and unioning
them is pure overhead. The fields are known at generation time and line up one-to-one, so
we can compare them directly. This is a **generated-class fast path**, exactly the kind of
optimization the perf convention allows (keep `Gn`/`base` clean; put speed in the generated
code — see the `perf-work-priorities` memory).

## The critical constraint — do NOT regress symbolic equality

The current path is **simplify-aware**: it treats coefficients as *mathematically* equal,
not *structurally* equal. A naive field comparison would break this, because `==` on
`sympy.Expr` is **structural**:

- `sympy` auto-canonicalizes some forms, so `sympify("a + b") == sympify("b + a")` is
  `True` — fine.
- But `(x + 1)**2 == x**2 + 2*x + 1` is **`False`** under bare `==` (needs `expand`/
  `simplify`). The generated classes don't eagerly simplify (that's their whole point), so
  same-type operands *can* hold structurally-different-but-equal symbolic coefficients — the
  README even calls this out (`.simplified()` / `.expanded()` exist for exactly this).

So the same-type fast path must apply the **same** `simplify(sympify(l) - sympify(r)) == 0`
test **per field** — it just skips the dict construction and key-union, not the
simplify-awareness.

## Plan

1. **Give `eq_method()` the field list** (like `iter_method(blades)` /
   `is_close_method(type_name, fields)` already take). `is_close_method` is the closest
   model — it already emits a `type(self) is type(other)` same-type, field-wise body; mirror
   its shape.
2. **Emit a same-type fast branch** at the top of `__eq__`, using `all([...])` over the
   fields (see decision 1):
   ```python
   if type(self) is type(other):
       return all([
           sympy.simplify(sympify(self.coeff_e_1) - sympify(other.coeff_e_1)) == 0,
           ...,  # one per field
       ])
   ```
   Use `type(self) is type(other)` (exact identity — every generated type is
   `@typing.final`, so no subclassing to worry about).
3. **Keep the existing blade-dict path as the fallback** for the cross-type / cross-
   representation cases (`Vector == G`, specialized `== Gn`, etc.) and keep the
   `isinstance(other, MultiVectorBase)` / `NotImplemented` guard first.
4. **Regenerate** (`make generate`) and re-run the suite + the determinism guard
   (`make check-generated`).

## Deferred follow-up — cheap-structural-first shortcut

**Not part of this task** (see decision 2). A later optimization: for each field, try the
cheap structural `self.coeff_e_1 == other.coeff_e_1` first and fall back to the
`simplify(...)==0` test only on mismatch — fast for equal-numeric/equal-structural cases,
still correct for the symbolic-but-unsimplified case. Ship the plain simplify-per-field
version first, measure, then decide whether this shortcut earns its complexity.

## Verification

- **Conformance/graded suites** (`test_conformance.py`, `test_graded.py`) exercise `==`
  broadly — they must stay green.
- **Add a targeted symbolic test**: two same-type values whose coefficients are
  mathematically equal but **structurally different** (e.g. one field `(x+1)**2`, the other
  `x**2 + 2*x + 1`) must still compare **equal** through the fast path. This is the
  regression the whole task hinges on — without it, the fast path silently weakens `==`.
- **Bench** (`tools/bench.py` or an ad-hoc `timeit`): confirm the same-type path is
  actually faster (and record the number), so the added generator complexity is justified.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-24)

1. **Emit `all([...])`** over the fields (not a chained `and`) — consistent across
   dimensions, tidy for 𝒢₅'s 32-field `G`.
2. **Ship the plain simplify-per-field version only.** The cheap-structural-first shortcut
   is a deferred follow-up (above), to be measured before adding.
