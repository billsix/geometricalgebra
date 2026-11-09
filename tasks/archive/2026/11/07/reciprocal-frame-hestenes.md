# Reciprocal frame, implemented as Hestenes & Sobczyk write it 

**Created:** 2026-11-04 · **Completed:** 2026-11-07

Implemented the **reciprocal frame** `a^1 … a^n` of a frame `a_1 … a_n`, the vectors with
`a^k · a_j = δ^k_j`. Requested by William Emerison Six <billsix@gmail.com>. The math, the explainer,
and the design choices live in `tasks/reference/frames-qr-and-reciprocal-frames.md`,
section "The relation to Hestenes' reciprocal frame".

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07)

- **The formula as the book writes it.** The maintainer read it from Hestenes & Sobczyk, *Clifford
  Algebra to Geometric Calculus*, p. 28:
  - eq (3.6): `A_n = a_1 ∧ … ∧ a_n`;
  - eq (3.7): `a^k = (−1)^(k−1) (a_1 ∧ … ǎ_k … ∧ a_n) A_n⁻¹`, a geometric product;
  - the result `{a^1, …, a^n}` is a Python list.
- **The property the tests cite** is eq (3.5), `a^k · a_j = δ^k_j` (Kronecker delta: 1 when `j = k`,
  0 otherwise), and only that one. The other checks are gacalc's own consistency tests.
- **Scope:** the request was the implementation and symbolic unit tests (2026-11-07). The three-forms
  rule's Lean theorem and book page were not part of it and were not written; the book's frames
  notebooks were not changed.

## What was done

- **`gacalc.frame.reciprocal_frame(vectors) -> list`**, written literally from eq 3.7:
  - `enumerate(frame, start=1)` makes the loop variable the book's `k`, so the sign is `(−1)^(k−1)`;
  - the face `a_1 ∧ … ǎ_k … ∧ a_n` is its own function, `all_wedged_except_the_kth(vectors, k)` (k from 1;
    `ValueError` outside `1 … n`), named at the maintainer's suggestion (2026-11-07); it slices out
    `a_k` and folds the rest with `functools.reduce(operator.xor, …)`;
  - it raises `ValueError` on a non-frame;
  - its docstring cites eqs 3.5–3.7 and carries the explainer's oblique example as a doctest
    (`a^1 = 1/2 e_1 − 1/6 e_2`, `a^2 = 1/3 e_2`, and the identity matrix).
- `itertools.combinations(vectors, n − 1)` was considered and rejected: it emits the faces leaving out
  the *last* vector first.
- **`Frame.reciprocal_vectors()`**: the same, as a tuple.
- **Tests:**
  - in `tests/test_frame.py`, on general symbolic 2D and 3D frames:
    - eq 3.5, as the identity matrix `[a^k · a_j]`;
    - each `a^k` has only a grade-1 part, which justifies reading eq 3.7's product as the dot;
    - the reconstruction `y = Σ (a^k · y) * a_k`;
    - `a^n = w_n / |w_n|²`;
    - an orthonormal basis is its own reciprocal;
    - `ValueError` on a dependent frame and on an empty one.
  - in `tests/test_frame_class.py`: the reciprocal coordinates `vⁱ · y` equal
    `Frame.to_invertible_function()`'s peel inverse (2D and 3D symbolic). This replaced the earlier
    `test_last_reciprocal_vector_is_the_last_rejection`, which computed `w_n / |w_n|²` by hand and is
    now covered in `test_frame.py`.
- `CHANGELOG.md` `[Unreleased]` entry; the explainer was folded into the reference doc.

## Follow-ons

- `tasks/frame-inverse-head-first-recursion.md` was blocked on this task and was unblocked by it.
