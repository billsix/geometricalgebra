# Show the reader which values typed `MultiVectorBase` are vectors

**Status:** proposed — needs go-ahead, and answers to the open questions
**Priority:** 5
**Difficulty:** 4 (the edits are small; choosing the rule and applying it evenly is the work)
**Created:** 2026-11-28 (William Emerison Six <billsix@gmail.com>: "for the reader who is new, they may not
know that for making a matrix, these are all vectors … write up a task … with the goal of thinking about how
to make the code more clear to the initial reader")

## BLUF

Dimension-generic code annotates its values `MultiVectorBase`, the widest type, even where every value is
known to be a vector. `to_matrix` in `src/gacalc/transforms.py` is the example the maintainer found: the image
of the origin and the images of the unit directions are vectors, the matrix is built from their coordinates,
and nothing on the page says so. Done means the maintainer has chosen a rule from the options below, the rule
is written into the project's coding standard, and the hand-written modules follow it, with `to_matrix` first.

## Context

**Read first:**

- `src/gacalc/transforms.py`, `to_matrix` (the lines binding `origin` and `directions`).
- `CLAUDE.md`, the rule "Check 'must be a vector' with the shared guard": `MultiVectorBase.require_vector(value)`
  and `require_vectors(values)` raise `ValueError` naming the caller; "never a bare `assert`" (it is gone under
  `python -O`).
- `tasks/reference/hestenes-variable-notation.md`: the naming rule already in force (Greek for scalars,
  lowercase Latin for vectors, CAPITAL Latin for higher grades, versors and general multivectors).
- `tasks/reference/gn-graded-typing-feasibility.md` and `tasks/gn-graded-typing-implement.md`: a `Vector`
  marker class for `Gn` was investigated on 2026-10-28. The verdict was "feasible, but do it only when a
  dimension-agnostic call site needs it"; the implementation task has waited for such a call site since.
- `tasks/typing-base-return-types-redesign.md` (parked): making the base class's return types true. It
  changes what a type checker infers for a sum or a product, which bears on the options here.

**Why the type is `MultiVectorBase` there.** `to_matrix(fn, cls, n)` takes `cls: type[MultiVectorBase]` and
`fn: ComposableFunction[typing.Any]`. In 𝒢₂ and 𝒢₃ the caller passes the generated `Vector` class, so at run
time `fn(cls.zero())` is a `Vector`; with `Gn` it is a `Gn` that happens to be grade 1, because `Gn` has no
graded subtypes. The annotation states the one type true for every caller. The module already has a type
variable, `V = typing.TypeVar("V", bound=MultiVectorBase)`, used by the transform factories; `to_matrix` does
not use it.

## What the scan found (2026-11-28)

Discovery command, from the repo root (it lists local bindings whose annotation is `MultiVectorBase` or a
list, tuple or sequence of it):

```
grep -nE '^\s+[A-Za-z_0-9]+: (list\[|tuple\[|Sequence\[)?MultiVectorBase[^=]*= ' <files>
```

- **Hand-written library modules** (`base.py`, `frame.py`, `gn.py`, `measure.py`, `standardposition.py`,
  `transforms.py`, `vectorcalc.py`): 35 such bindings. Read one by one, they fall into four kinds:
  - **vectors:** `origin` and `directions` in `to_matrix`; the four `shadow` bindings in `transforms.py`
    where a vector is projected onto or rejected from a vector (two more project onto or reject from a plane,
    and are vectors too); `e_1`, `e_2`, `e_3` and `projected_in_standard_position` in `standardposition.py`;
    `others` and `orthogonal_vectors` in `frame.py`.
  - **bivectors or blades:** `plane` (twice in `transforms.py`), `wedge` (`measure.py`, `vectorcalc.py`),
    `blade` and `A_n_inverse` (`frame.py`).
  - **versors and rotors:** `versor`, `versor_inv`, `rotor` (twice), and `product` in `base.py`.
  - **general multivectors**, where `MultiVectorBase` is the right word: the `sum(...)` results in `base.py`
    and `gn.py` (`inner`, `outer`, `contraction`, `product`), `conjugated`, `projected`, `rejected`.
- **`src/gacalc/nbplotutils.py`:** 30 bindings, nearly all vectors by meaning (`ex`, `ey` six times each,
  `origin`, `vertices`, `label_offset`, the `…_direction_world_space` names). The module calls a guard or
  raises in six places.
- **Tests, examples, the book and the notebooks:** 237 lines match the same pattern. They were counted, not
  read.
- **Parameters:** `transforms.py` has 46 `MultiVectorBase` annotations in all, 13 of them local bindings; the
  rest are mostly parameters, and a parameter that must be a vector is already guarded by
  `require_vector`/`require_vectors` in the functions read (`project`, `reject`, the rotation factories).
- **The generated modules** (`g1.py`, `g2.py`, `g3.py`) have no such local binding; their `MultiVectorBase`
  annotations are parameters of the generated overloads. They are out of scope.

So the question is wider than vectors: a reader also cannot tell from the type that `plane` is a bivector or
`rotor` a rotor. Vectors are the largest group and the one the maintainer named.

**What the docs and the archive already hold.** No reference doc, open task or archived task addresses how a
known-grade value should read at the place it is bound. The nearest are the ones under "Read first", and
these archived tasks about the guard itself: `tasks/archive/2026/11/06/consolidate-vector-grade-checks.md`,
`tasks/archive/2026/11/06/reuse-existing-vector-check.md`,
`tasks/archive/2026/11/10/require-guards-caller-frame-context.md` and
`tasks/archive/2026/10/28/gn-graded-typing-subclasses.md`.

## Options

The first three are the maintainer's; the fourth and fifth came out of the scan.

1. **A vector class for `Gn`, and narrow to it.** With `class Vector(Gn)` and a narrowing helper
   (`tasks/gn-graded-typing-implement.md`, design (A)), `Gn` code could bind `origin: Vector`.
   - For: the type says "vector" and a type checker holds the code to it.
   - Against: it does not reach `to_matrix`, which is generic over `cls` and must also serve 𝒢₂ and 𝒢₃; the
     annotation there would still be the common base. It helps only code written for `Gn` alone.
   - This task would be the first real call site that the implementation task has been waiting for, if any
     `Gn`-only site turns up in the worklog.
2. **Guard, and say so in a comment.** After the binding: `MultiVectorBase.require_vectors([origin,
   *directions])`, with a comment that the values are typed `MultiVectorBase` only because the function serves
   every dimension, and are vectors.
   - For: it is the project's existing idiom; the reader sees the word "vectors"; and in `to_matrix` it is a
     real check, since a transform that maps a vector to a non-vector would otherwise produce a wrong matrix
     silently (`coords` reads only the grade-1 coefficients).
   - Against: it costs a run-time pass per call, and by the project's rule it is a call that raises, never an
     `assert`. For values a function has just built from `basis_vector`, the guard checks what cannot fail.
3. **Put the kind in the name:** `direction_vectors`, `origin_vector`, `plane_bivector`.
   - For: free at run time, and visible at every use, not only at the binding.
   - Against: `tasks/reference/hestenes-variable-notation.md` already encodes the grade in the name's case
     (lowercase for a vector, CAPITAL for higher grades). A second encoding beside it needs a rule for when
     to use which. That doc counts "descriptive multivector words" (its example is `plane`) as conforming, which is why
     `plane`, `wedge`, `versor` and `rotor` are lowercase without being vectors: for a descriptive word the
     case says nothing, and the word itself has to carry the kind. `directions` and `origin` are such words,
     and they do not say "vector".
4. **Make the signature generic where the caller passes the vector class.** `to_matrix(fn:
   ComposableFunction[V], cls: type[V], …)` lets the bindings read `origin: V` and `directions: list[V]`, and
   the docstring says once that `V` is the algebra's vector type.
   - For: true for every caller, checked by `ty`, and in 𝒢₂ and 𝒢₃ a call site's inferred type becomes
     `Vector`.
   - Against: `V` is no clearer to a new reader than `MultiVectorBase` unless the docstring explains it, and
     `fn(e_i) - origin` is typed by the base class's operators, so the parked return-types task decides
     whether `ty` accepts `list[V]` without a cast.
5. **A type alias that names the meaning:** `VectorLike: TypeAlias = MultiVectorBase` ("a value of grade 1,
   in whichever representation"), used in annotations as documentation.
   - For: one word at the binding, no run-time cost, works in generic code.
   - Against: a type checker treats it as `MultiVectorBase`, so it can state a falsehood without anyone
     noticing; the project has so far preferred types that are checked.

**Agent's recommendation, to be confirmed:** combine 2 and 3 by where the value comes from. A value that
arrives from outside the function (a parameter, or the result of a caller's function, as in `to_matrix`) gets
the guard and the comment. A value the function builds itself keeps no guard and gets a name that follows
the Hestenes rule, lengthened with the kind only where the short name misleads. Leave option 1 with its own
task, and try option 4 on `to_matrix` alone to see what `ty` says before deciding on it.

## Plan

1. Answer the open questions; record the decisions here.
2. Write the worklog: run the discovery command over the hand-written modules, `nbplotutils.py`, the
   examples, tests, book sources and notebooks; save the output under
   `tasks/adhoc/show-the-grade-of-values-typed-multivectorbase/data/` and mark each line vector, bivector,
   versor or general, by reading it.
3. Apply the chosen rule to `to_matrix`, run the gate, and show the maintainer the before and after of that
   one function before going further.
4. Apply it to the rest of the hand-written library modules, then to `nbplotutils.py`. Generated code,
   doc-region markers and doctest output stay as they are.
5. Write the rule into `tasks/reference/python-coding-standard-gacalc.md`, with `to_matrix` as its example,
   and add a line to `tasks/reference/hestenes-variable-notation.md` if names change. Add a `CHANGELOG.md`
   entry only if a public name or signature changes (option 4 changes `to_matrix`'s signature).

## Open questions

1. Which rule: the agent's recommendation (guard values that come from outside, name values built inside), or
   one of options 1 to 5 alone? (name it)
2. Scope: vectors only, or every known-grade value (bivectors such as `plane` and `wedge`, rotors and versors)?
3. Do the tests, examples, book sources and notebooks (237 lines) follow the same rule, or only the library
   modules a reader meets first?
4. May a name carry its kind (`direction_vectors`) where the Hestenes case rule already marks it, or only
   where the short name misleads?
