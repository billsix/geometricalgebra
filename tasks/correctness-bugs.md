# Correctness bug fixes (backlog)

Status: **not started** · proposed 2026-06-04 · needs go-ahead per item

Real correctness issues identified during the initial assessment (see `CLAUDE.md` "Assessment").
They were reported, not fixed (never authorized). Each is small. Grouped here for one review.

## 1. `reject` / `reflect` sequence handling (`base.py`)

Both `AbstractMultiVector.reject` and `.reflect` handle a `Sequence` argument by calling
`cls.outer_product(*sequence)`. But `outer_product` is an **instance** method `(self, rhs)`, so this
only works by luck for **exactly two** elements (it becomes `outer_product(seq[0], seq[1])`); 1 or 3+
elements break. `project` does it correctly via `outer_product_of_vectors(*onto)`.
**Fix:** make `reject`/`reflect` use `cls.outer_product_of_vectors(*sequence)` too.
Covered by tests? `test_project_and_reject` only exercises the 2-element case, so add a 3-element
(or 1-element) case when fixing.

## 2. Suspicious `__rmul__` negation (`base.py`)

`AbstractMultiVector.__rmul__` fall-through returns `-self._geometric_product(lhs)`. The geometric
product isn't anticommutative in general, so the negation looks wrong. It appears to be **dead code**
(scalars are handled by the earlier match arms; MV*MV goes through `__mul__`). **Fix:** confirm it's
unreachable and either remove the branch / `return NotImplemented`, or correct it. Verify no test or
notebook relies on it first.

## 3. Test copy-paste bug (`tests/test_multivector.py`)

In `test_multivector_unit_pseudoscalar`, `i15` is built with `unit_pseudoscalar(14)` instead of
`unit_pseudoscalar(15)` (then asserts `i15 * i15 == -one`). The grade-15 case is therefore never
tested. **Fix:** change `14` → `15` and confirm the assertion still holds (𝒢₁₅ pseudoscalar squares
to −1).

## Open questions

- Fix all three now, or just #1 and #3 (clear wins) and leave #2 pending a closer look at whether
  the branch is truly dead?
