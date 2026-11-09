# Thin pass-through instance methods for project / reject (apply-to-this-value sugar)

**Created:** 2026-08-25 · **Completed:** 2026-08-26

This is the design record (rationale, boundary, call-site sweep). The implementation shipped as
Tier 3 of `tasks/archive/2026/08/26/precise-typing-remaining-methods.md`; see that doc for the typing
mechanism and verification.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-25 and 2026-08-26)

- **Names: `projected_onto` / `rejected_away_from` / `reflected_across`** (past participle,
  value-returning), each mirroring its factory's exact keyword (`onto` / `away_from` / `across`).
  `reflected_across` was included for symmetry with the factory trio. The first draft's
  `rejected_from` / `reflected_in` were renamed on 2026-08-26: they dropped the factory's
  preposition, and "rejected from" misreads as "excluded from".
- **Built inside the precise-typing task, not as a standalone ship**, so the pass-throughs and their
  precise graded return types arrived together (reusing the overload machinery already built for the
  `project`/`reject` factories) and `Vector.rejected_away_from(b)` was a `Vector` statically from day
  one, with no interim `-> MultiVectorBase` version to revise.
- `content_by_rejection` was unrelated (the doctest task) and was ignored here.

## Why (the maintainer asked whether this was useful; the answer was yes)

`project` / `reject` / `reflect` are classmethod factories returning a `ComposableFunction`, so
applying one to a value read verbosely — worst in `make_orthogonal_frame` (`src/gacalc/frame.py`),
whose inner loop was `w = type(w).reject(away_from=prior)(w)`. With the pass-through it became
`w = w.rejected_away_from(prior)`. Reasons it was the right call:

1. **Precedent in this codebase:** `CLAUDE.md` (Architecture › measures) already has fixed-arity
   measures as thin pass-through methods on `MultiVectorBase` (`v.area(w)`) for discoverability.
2. **Many call sites were immediate applications**, not factory reuse — the
   `Cls.project(onto=b)(a)` shape throughout `tests/` and `notebooks/` (e.g. `notebooks/displayg2.py`
   `a_par = Vector.project(onto=b)(a)`), plus `frame.py`.
3. **Zero cost to the existing design** (see the boundary below).

## The change

Three value-returning methods on `MultiVectorBase` (`src/gacalc/base.py`), e.g.
`def rejected_away_from(self, away_from) -> ...: return type(self).reject(away_from)(self)`. One
definition is inherited by `Gn` and every generated type, so no per-type emission was needed for the
behaviour. `type(self).…` (not `MultiVectorBase.…`) was used so the generated types' own overrides
run and the runtime result keeps the concrete type.

**Where:** `base.py`, not per generated type or on `gn` only — it is representation-agnostic and
delegates to `type(self).project/reject`.

## The boundary — the factories stay

The pass-through is only for "apply once to this value"; the maintainer asked to keep the originals.
The factories remain required wherever the function itself is the object: composed into a pipeline
or wrapped in a labelled `ComposableFunction` (`transforms.py`, `base.reflect`'s own
`project`+`reject` split, the notebooks' `ComposableFunction(Gn.project(...), "P_{…}")`), used as a
Cayley-graph edge in github.com/billsix/modelviewprojection (needs the `InvertibleFunction`), or
assigned and reused. The change was purely additive: no signature of `project`/`reject`/`reflect`
changed.

## Call-site sweep

Converted: `frame.py` (`make_orthogonal_frame`). Deliberately not converted: `transforms.py`,
`base.reflect`, and the test/notebook sites that keep the function object, plus the
`assert_type`/typing tests that exercise the factory form. The wider one-shot sweep (e.g. the
`notebooks/displayg2.py` one-shots) was left undone as optional.

## Verification

Pass-through tests (`v.rejected_away_from(b) == reject(b)(v)` plus `assert_type` narrowing) were
added in `tests/test_dot_wedge_projection_split.py`; `make test` and `make format` were green (see
the precise-typing doc for counts).
