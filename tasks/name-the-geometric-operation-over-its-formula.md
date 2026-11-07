# Write the named geometric operation (project, reject, …) where code computes its formula by hand

**Status:** ready — the maintainer approved the candidate list (William Emerison Six <billsix@gmail.com>,
2026-11-07); not started
**Priority:** 4
**Difficulty:** 4
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>)

## BLUF

The maintainer wants gacalc's code to show a student how the math works, ahead of raw speed: "I think
'project' and 'reject' make much more sense to a student, than using the dot product directly." Replace
the hand-written dot-product formulas listed below with the named operation they compute, with no change
in results, and add the rule to `CLAUDE.md`. Done = the four sites changed, every test still passing,
`make format` green, the 3D symbolic test time measured before and after, and the rule written.

## Context

- The operations: `MultiVectorBase.project(onto)` / `reject(away_from)` in `src/gacalc/base.py`. They are
  **factories**, `cls.project(onto)(value)`, with pass-through sugar on values (see the comment block
  "project/reject/reflect pass-through sugar" in `base.py`). `P_B(A) = (A · B) * B⁻¹`, H&S eq 2.9.
- The survey (2026-11-07) covered `src/gacalc/` (hand-written modules), `book/docs/notebooks/`,
  `notebooks/` and `book/figures/epix/`. The generated `g1`–`g3` modules were left out: they are the fast
  path by design, and `Gn` is the readable reference.
- The frame math the first two sites compute: `tasks/reference/frames-qr-and-reciprocal-frames.md`.

## The sites to change

1. **`Frame.coefficients()` and the peel step of `Frame.to_invertible_function`** (`src/gacalc/frame.py`)
   compute `(w · v) / |w|²` with `_exact_quotient`. That number is "how many copies of `w` the projection
   of `v` onto `w` is": `project(v, onto=w) = c * w`. Read `c` off as the quotient of two parallel vectors,
   `(project(v, onto=w) / w).scalar_part()`, which is a scalar. If that reads awkwardly at both sites,
   add one small named helper for it (one definition shared by two callers meets the extraction bar).
   Keep exactness: ints and sympy must stay exact, float stays float (CLAUDE.md, `magnitude`/`inverse`).
   **Measure** the 3D symbolic tests in `tests/test_frame_class.py` before and after (about a minute today);
   report the change in the done-record.
2. **The book notebooks** `book/docs/notebooks/frame-qr-2d.py` and `frame-qr-3d.py` compute the same
   `(w · y) / |w|²` five times (`x_1`, `x_2`, `x_3` steps). They are the most student-facing of the four;
   use the same form as site 1, and adjust the surrounding markdown so the prose says "projection" where
   the code does. The prose's "two heights, one divided by the other" reading stays true; keep it if it
   still fits.
3. **The forward map's `x.dot(cls.basis_vector(i)).scalar_part()`** (`frame.py`) becomes
   `x.coefficient(cls.basis_vector(i))`: the i-th coordinate, said directly.
4. **The book's projection figure helper** `_project_point` in `book/figures/epix/_projection_scene.py`
   recomputes `((a·b)/(b·b)) b` from raw coordinates. Build gacalc vectors from the two points, call
   `project`, and convert the result back to an ePiX `Point`, so the figure is drawn by the operation it
   illustrates. Keyword arguments throughout (the figure rule in CLAUDE.md); check `make docs` renders it.

**Also fix in `reflect`** (`base.py`), found during the survey: the bare `assert value.is_vector()` becomes
`MultiVectorBase.require_vector(value, "reflect")` (CLAUDE.md: never a bare `assert`), and the default
branch's `raise Exception("TODO - implement project for " + …)` names the wrong function and raises a bare
`Exception`; make it a `ValueError` naming `reflect` and the grades it accepts. Add a `CHANGELOG.md`
`[Unreleased]` entry, since the exception type changes.

## Left alone, and why

- The definitions themselves: `project`/`reject`, `cross` (`(a ∧ b) * I₃⁻¹`), `sandwich`, `exp`,
  `cosine` (`Ã ∗ B`, H&S eq 1.53b, defined for blades), the measures' wedge-and-dual. These are the
  primitives the other code should call.
- Code that already uses the named operations: `reflect` (`project − reject`), `projection_rotation`,
  `make_orthogonal_frame` (Gram–Schmidt by `reject`).
- The reciprocal inverse `vⁱ · y`: that dot product is eq 3.5 itself, explained in the reference doc's
  similar-triangles section.
- The rotor built from `cos(θ/2)`/`sin(θ/2)` in `transforms.py`: it follows the sine/cosine presentation
  rule.
- Notebooks whose subject is the dot product (`notebooks/displayg2.py`/`displayg3.py`
  `a·b + a∧b = ab`, the Lagrange identity cells): the dot product is what they teach.
- `standardposition.py`: the deliberate standard-position duplicate.

## The `CLAUDE.md` rule

Add under "Conventions the agent must obey while writing code", next to the dot-product rule:

> **Write the named geometric operation where the code means it** — `project`, `reject`, `reflect`, a
> rotation factory, `coefficient` — not the dot-product formula it reduces to, even when the formula is
> faster. The code is read by students; the generated `g*.py` classes are where speed lives. The
> primitives' own definitions are the exception. (William Emerison Six <billsix@gmail.com>, 2026-11-07)

## Plan

1. Record the 3D symbolic test time on the current code.
2. Sites 1 and 3, then the full `make test`; measure again.
3. Site 2, then site 4 with `make docs`.
4. The `reflect` fixes with a test that a non-vector raises `ValueError`.
5. The `CLAUDE.md` rule; `make format`.

## Open questions

None.
