# Notebook demo: dot = projected geometric product, wedge = rejected (2D + 3D)

**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Done:** 2026-11-19

The maintainer asked, verbatim: *"See if in the notebooks, for at least 2D and 3d, see if I can show
that the dot product of a and b is the geometric product of a and b projected onto a. Same thing for
wedge, but rejected. See if I can do the same for 3d."* The math was already proved
(`tasks/reference/dot-wedge-projection-rejection.md`; Lean `G2.mul_proj_eq_dot`,
`G2.mul_reject_eq_wedge`, `G3.mul_proj_eq_dot`, `G3.mul_eq_proj_dot_add_reject_wedge`), so the task
was demonstration only.

## What was done

- **2D, demo notebook:** already present before the task started, in `notebooks/displayg2.py`
  (commit `adb4b1d`, 2026-08-03), and moved on 2026-11-18 to `notebooks/displayg2areas.py`, in the
  section "Which part of a makes the dot, and which the wedge?". It projects `a` onto `b` and
  multiplies on the right.
- **2D and 3D, book:** `book/docs/notebooks/projection.py` and
  `book/docs/notebooks/projection-rejection-3d.py`, filled by
  `tasks/archive/2026/11/19/fill-remaining-placeholder-book-notebooks.md`.
- **3D, demo notebook:** a new section in `notebooks/displayg3.py`, "Which part of b makes the dot,
  and which the wedge?", placed before "Each part on its own number line". It uses
  `a = 1 * e_1 + 2 * e_2 + 2 * e_3` and `b = 2 * e_1 + 1 * e_2 + 3 * e_3`, which lie on no axis or
  plane. The cells show that `proj + rej - b` is 0; that `a * proj_a(b)` and `a · b` are both 10; that
  `a * rej_a(b)` and `a ∧ b` are both `-3 e12 - 1 e13 + 4 e23`; and that the sum minus `a * b` is 0.
  The two products each get a `show_mult` table. The cell carries the twin comments for the two G3
  theorems.

## Decisions

- **Q1, where the 3D cells go** (William Emerison Six <billsix@gmail.com>, 2026-11-19): in
  `notebooks/displayg3.py` as well as the book.
- **Q2, the base vector** (William Emerison Six <billsix@gmail.com>, 2026-11-16): project onto `a`
  and multiply by `a` on the left, `a · b = a * proj_a(b)` and `a ∧ b = a * rej_a(b)`, stated as
  results. The 3D demo uses this form. The older 2D demo section keeps its project-onto-`b`,
  right-multiplied form, which is the same theorem with the roles swapped.
- `projected_onto` / `rejected_away_from` on the full `G` class are typed `MultiVectorBase`, so the
  two parts are annotated that way rather than cast to `G`.

## Verification

The notebook executed through nbconvert with every check printing 0. `entrypoint/format.sh` exited 0,
`pyright notebooks/` reported 0 errors, and `tools/check_annotations.py` reported no rows for
`displayg3.py`.
