# Python coding standard — geometricalgebra (gacalc) specifics

**Reference document.** gacalc's own worked examples and repo-specific details for the shared
cross-project Python standard. Read this *together with* the shared doc
`runClaudeInContainer/tasks/reference/python-coding-standard.md` (canonical:
github.com/billsix/runClaudeInContainer): the shared doc holds the portable rules; this doc
holds gacalc's worked examples, file paths, and type-layer specifics. Moved out of the shared
doc on 2026-10-12 so that doc stays portable (William Emerison Six <billsix@gmail.com>). Each
section names the shared rule it illustrates. Update in place.

## Reduce with `sum`/`math.prod` — worked example

Illustrating the shared "Reduce with `sum`/`math.prod`, not a hand-rolled accumulator loop"
rule: `measure.content_by_rejection` went from

```python
result = 1
for pv in make_orthogonal_frame(vectors):
    result = result * pv.magnitude()
```

to `math.prod((pv.magnitude() for pv in make_orthogonal_frame(vectors)), start=1)`. The `int`
identity `start=1` keeps a float/sympy pipeline intact (`1 * 2.0 == 2.0`).

## Annotation sweep — gacalc specifics

Illustrating "annotate every binding": gacalc's repo-wide annotation sweep landed 2026-09-09,
so every remaining unannotated site is a deliberate exemption catalogued in
`tasks/reference/type-annotation-exemptions.md`. Re-run `python tools/check_annotations.py`
after reshaping hand-written Python — a row it reports that is **not** in that doc is a
genuine gap, not noise.

## Parameterize generics — gacalc specifics

Illustrating "never a bare generic in an annotation": `ComposableFunction` / `InvertibleFunction`
are **invariant with an unbounded `V`** because `functions.py` must not import `base`. So:

- a value of exact type takes that type (`InvertibleFunction[g3.Vector]`);
- a *polymorphic* param that accepts any instance and applies it to the base internally takes
  `[Any]` — invariance makes a fixed base-parameter reject concrete-typed arguments, and a
  bound TypeVar reject the internal base-application, so `Any` is the only thing compatible
  both ways;
- the notebooks aren't in the `ty` gate — verify their generics with `pyright` in the
  container, where the host `ty` can't reach.

Detail: `tasks/reference/transform-and-composable-function-layer.md`,
`tasks/reference/generated-product-typing.md`.

## What earns an extraction — gacalc worked examples

Illustrating the shared "What earns an extraction: duplication, or naming a phase" rule.

**Module-level, because more than one caller needs it.** `nbplotutils._to_xy` replaced the
same 79-char lambda written out **9 times across 5 functions**; `_draw_labelled_triangle`
replaced three 58-line, 91–93%-identical `draw_*_triangle` helpers with one function plus
three ~10-line callers (**net −75 lines**, all rendered figures verified pixel-identical). A
private nested helper in each of the five would have been five copies — worse than the
duplication it "fixed".

**Nested, because it closes over the enclosing parameters and names a phase.** `base.reject`'s
`r`/`rejection` close over `away_from`; `_route` splits into `breadth_first_parents` /
`walk_back`, both over `a` and `b`.

**"Inner-fn first, guards below" is a consequence, not the goal.** When an extraction is
earned, the guards naturally end up at the bottom calling into it — as in `base.reject`:

```python
def reject(cls, away_from):
    def r(value):  # the core operation, up top
        return value.wedge(away_from) * away_from.inverse()

    def rejection(blade):  # wraps it with its LaTeX label
        return ComposableFunction(r, latex_repr=..., linearity=Linearity.LINEAR)

    match away_from:  # preconditions / dispatch below, calling in
        case [*sequence]:
            return cls.reject(cls.outer_product_of_vectors(*sequence))
        case MultiVectorBase() as vector if vector.is_vector():
            return rejection(vector)
        case _:
            raise ...
```

A related lesson: an error is best raised by the code that *discovers* it — `_route`'s "no
path" moved into the search itself, which is what let its tail collapse to one line.

## Inline once, declare at use, nest and shadow — `Frame.to_invertible_function` (2026-11-06)

Illustrating the shared "Inline a value used once, and name it in a comment instead of a binding"
rule and the "nest a helper with one caller / shadow deliberately" bullets. Before (abridged):

```python
frame_vectors: Sequence[MultiVectorBase] = self.vectors        # an alias
k: int = len(frame_vectors)
cls: type[MultiVectorBase] = type(frame_vectors[0])            # used once
dimension: int | None = getattr(cls, "DIMENSION", None)
n: int = (
    dimension
    if dimension is not None
    else max(max(blade) for v in frame_vectors for blade in v.to_blade_dict() if blade)
)
...
pairs = tuple(zip(self.orthogonal_vectors, frame_vectors, strict=True))  # used 40 lines later
def peel(remaining, y): ...        # only backward calls it
def backward(y): ... peel(pairs, y) ...
```

After:

```python
# n is the dimension of the space.  type(self.vectors[0]) is the frame's representation: a
# specialized type fixes n as its DIMENSION; Gn has none, so the getattr default gives the
# smallest dimension holding every frame vector.
n: int = getattr(
    type(self.vectors[0]),
    "DIMENSION",
    max(v.implied_minimal_number_of_dimensions() for v in self.vectors),
)
if len(self.vectors) != n:
    raise ValueError(f"... got k = {len(self.vectors)} vectors in n = {n} dimensions")
...
def backward(y):
    def peel(remaining, y): ...    # y deliberately shadows backward's y
    ...
    # The tuple(zip(...)) argument to peel is the pairs: each orthogonal vector with the
    # frame vector it came from, (w_i, v_i), in frame order.
    ... peel(tuple(zip(orthogonal_vectors, self.vectors, strict=True)), y) ...
```

What each change shows:

- `cls`, the `frame_vectors` alias, and `pairs` were single-use: inlined, with a comment naming
  `pairs`.
- `dimension` was used twice, but only as "value or fallback", which `getattr`'s default already
  does. `k` was used twice, but `len(self.vectors)` is cheap to repeat. Both went away.
- `n` is used twice (the check and its message) and its expression is three lines, so it keeps its
  name (the maintainer's call).
- The opaque nested `max(max(blade) …)` became the named method
  `MultiVectorBase.implied_minimal_number_of_dimensions()`, which also replaced
  `measure._max_basis_index`.
- `peel` moved inside `backward`, its only caller. Its `y` shadows `backward`'s `y` on purpose:
  `peel` only ever reads its own `y`, and none of its other names (`remaining`, `earlier`, `w`,
  `v`, `x_last`) bind anything in the enclosing scopes.

Record: `tasks/archive/2026/11/06/refactor-frame-to-invertible-function.md`.

## Tests: parametrize over the variants — gacalc worked examples (2026-11-07)

The shared standard's "Tests: parametrize over the variants, don't copy the test" applied here (record:
`tasks/archive/2026/11/07/tests-parametrize-variants-and-dimensions.md`):

- `tests/test_frame.py` `FRAMES` / `FRAME_IDS`: one list of frames (symbolic 2D/3D on `Gn`, a concrete
  3D frame, concrete frames on graded `g2`/`g3`) that every orthogonalization and reciprocal-frame test
  runs over. Each frame list is annotated `list[MultiVectorBase]` so the mixed list type-checks.
- `tests/test_frame.py` `PREFIX_BLADE_CASES`: `(vectors, expected)` pairs with the expected prefix
  blades written out, so the test does not restate `prefix_blades`' own fold.
- `tests/test_frame_class.py`: the 2D and 3D maps under each inverse method are module-scoped fixtures
  (`function_2d`, `function_2d_peel`, `function_3d`, `function_3d_peel`) picked by name with
  `request.getfixturevalue`, because a 3D symbolic map takes about a minute to build. The graded round
  trip stacks a frame `parametrize` on an `INVERSE_METHODS` one.
- **Kept apart on purpose:** `tests/test_dot_wedge_projection_split.py`'s
  `test_geometric_product_splits_into_dot_and_wedge_{2d,3d}` (each spells out its own formula as a
  worked example), the `typing.assert_type` tests in that file, and
  `tests/test_sandwich_grades.py`'s `test_versor_sandwich_fixes_pseudoscalar_{2d,3d}` (each annotates
  its own static return type).

## Symbolic tests write their vectors inline (2026-08-25; scope settled 2026-11-09)

A symbolic test writes its general vectors inline, with the exact expected formula next to them
(`a: Vector = a_1 * e_1 + a_2 * e_2`, then the expected coefficients spelled out), so a reader sees
what is being checked. It does not import shared `sym_vec_*` fixtures from `gacalc.gn` or hide its
inputs behind module-level constants (decided in
`tasks/archive/2026/08/25/explicit-symbolic-tests-and-helper-cleanup.md`).

A `parametrize` over **named variants** is still fine (the 2026-11-07 section above), as long as each
variant is written out inline in the parameter list or in one list beside the test, like
`tests/test_frame.py`'s `FRAMES`. The rule is against inputs a reader has to look up elsewhere, not
against running one test over several inputs. (William Emerison Six <billsix@gmail.com>, 2026-11-09,
choosing the reviewer's recommendation in `tasks/review/2026/11/08/repo-review.md` §1.1.)

## Notebooks show values with `display(...)`, never `print`

The demo and book notebooks render a value with IPython's `display(...)` (or a cell's last expression),
not `print`. `display` shows the LaTeX form (`_repr_latex_`); `print` shows the plain repr. ruff's
`T201` enforces it (`tasks/archive/2026/09/05/fix-make-format-ruff-errors.md`).

## Cross-links (gacalc)

- `tasks/reference/conditional-refactoring-rules.md` — the Rules A–E worked examples.
- `tasks/reference/type-annotation-exemptions.md` — the catalogued no-annotation sites and
  their reasons.
