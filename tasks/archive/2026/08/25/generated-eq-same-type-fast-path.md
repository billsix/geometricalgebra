# Generated `__eq__` — same-type field comparison instead of always via blade dict

**Created:** 2026-08-24 · **Completed:** 2026-08-25

## Background

Every generated value type (the full `G` and the graded subtypes) shared one `__eq__`, emitted by
`eq_method()` in `tools/gen_specialized.py`. It always round-tripped both operands through the
blade-dict interchange, unioned the key sets, and tested each blade with
`sympy.simplify(sympify(l) - sympify(r)) == 0`. For the common same-type case (`Vector == Vector`,
`G == G`) the fields are known at generation time and line up one-to-one, so the dicts and key unions
were pure overhead. A generated-class fast path fits the performance convention: keep `Gn`/`base` clean
and put speed in the generated code.

**The constraint: do not regress symbolic equality.** The existing path is simplify-aware
(mathematical, not structural, equality). `==` on `sympy.Expr` is structural, so
`(x + 1)**2 == x**2 + 2*x + 1` is `False`, and the generated classes don't eagerly simplify, so
same-type operands can hold structurally different but equal coefficients (the README's
`.simplified()` / `.expanded()` exist for this).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-24)

1. **Emit `all([...])` over the fields**, not a chained `and`: consistent across dimensions and tidy
   for 𝒢₅'s 32-field `G`.
2. **Ship plain simplify-per-field first** and defer a cheap-structural-first shortcut until
   measured. **This was reversed by measurement** (below).

## What changed

- `eq_method` takes the field list (modelled on `is_close_method`, which already emitted a same-type,
  field-wise body) and is wired at both call sites: `class_header_stmts` (the full `G` and graded
  types) and `generate_scalar` (each algebra's `Scalar`).
- The emitted `__eq__` keeps the `isinstance(other, MultiVectorBase)` / `NotImplemented` guard first,
  then a `type(self) is type(other)` branch (exact identity is safe, since every generated type is
  `@typing.final`), then the blade-dict path as the cross-type / cross-representation fallback
  (`Vector == G`, specialized `== Gn`).
- **The same-type branch uses the cheap-structural-first shortcut:** per field,
  `self.coeff_X == other.coeff_X` **or** `simplify(sympify(l) - sympify(r)) == 0`. Native `==` comes
  first (exact and instant for numeric and same-form symbolic values); simplify runs only on a
  structural mismatch.

## Why decision 2 was reversed

The plain simplify-per-field version benchmarked **2.3× slower** for a low-grade value held in the full
`G` (sparse): the dense per-field `simplify(0-0)` ran on zero fields that the sparse blade-dict path
skipped, and sympy dominated. The maintainer's insight resolved it: sympy dominated only because every
field went through `sympify` + `simplify`, even plain int/float, while the numeric case (the
specialized classes' whole point) should use native `==`.

- **Bench:** numeric same-type `==` **0.34 µs**, vs ~18.5 µs all-sympy (~54×) and 5.7 µs for the sparse
  dict fallback (~17×). Symbolic different-form comparison was unchanged (~1.2 ms) and still correct.
- **Floats stay exact** (`0.1+0.2 != 0.3`): a native `==`, not a tolerance. Tolerance is `isclose`'s job
  (the generator already emits it on every type, plus `MultiVectorBase.isclose`; no gap), and a
  tolerant `==` would not be transitive.
- Semantics were unchanged from the old all-sympy `__eq__`.

## Verification

Regenerated g1–g3; full suite **405 passed**, including the new regression test
`tests/test_graded.py::test_same_type_eq_fast_path_stays_simplify_aware` (structurally different but
equal coefficients, such as `(x+1)**2` and `x**2 + 2*x + 1`, still compare equal); conformance and
graded suites green; generator output byte-identical across regeneration.
