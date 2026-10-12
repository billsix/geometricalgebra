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

## Cross-links (gacalc)

- `tasks/reference/conditional-refactoring-rules.md` — the Rules A–E worked examples.
- `tasks/reference/type-annotation-exemptions.md` — the catalogued no-annotation sites and
  their reasons.
