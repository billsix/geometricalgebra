# Part I projection and rotation notebooks: rewrite their checks in the Part III style

**Status:** proposed — needs go-ahead (Open questions below block implementation)
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-16 (William Emerison Six <billsix@gmail.com>)
**Related:** `tasks/bootstrap-dot-wedge-from-proj-rej.md` (wrote the cells the maintainer pointed
to as the model); `tasks/archive/2026/11/09/book-rotate-chapter.md` and
`tasks/archive/2026/11/09/book-restructure-parts.md` (wrote the Part I notebooks in question)

## BLUF

The maintainer, 2026-11-16, on the cells added to `book/docs/notebooks/bootstrap-projection.py`
and `bootstrap-product.py`: those are the kind of derivation checks they want evaluated in the
book, "the perfect style to do instead of" what earlier projection and rotation material did,
which "subtracted stuff to make sure they equal zero". Done means the Part I projection and
rotation material checks its math in that style, and the style is written down in
`tasks/reference/book-outline.md` so new notebooks follow it.

## Context

### The model style (Part III, 2026-11-16)

From `book/docs/notebooks/bootstrap-product.py`:

```python
# %% [markdown]
# ## Dot and wedge through projection and rejection
#
# `a * proj_a(b)` is the dot product and `a * rej_a(b)` is the wedge. ...

# %%
projection: Vector = b.projected_onto(a)
rejection: Vector = b.rejected_away_from(a)
zeros(a * projection - a.dot(b))  # -> [0, 0]
```

- Each result has its own markdown heading, worded the way the page states it (and naming the
  page's equation).
- Each code cell checks one identity, and its last line is the check, so the evaluated book shows
  its output (`[0, 0]`).
- One small `zeros` helper per notebook; the named operations (`projected_onto`,
  `rejected_away_from`, `rotate_90_degrees`) rather than formulas.

### What the earlier material does (inventory 2026-11-16)

None of the book's `.rst` pages does a subtract-to-zero check. They all live in the companion
notebooks (`grep` for "difference", "subtract" and "zero" in `book/docs/*.rst` found nothing
relevant). The Part I projection and rotation notebooks mix three styles:

| Notebook | Lines | `assert` | inline `sympy.simplify(sympy.sympify(…))` | `symbolically_equal(…)  # -> True` |
|---|---|---|---|---|
| `rotate.py` | 59 | 3 | 0 | 0 |
| `product-from-projection.py` | 88 | 6 | 3 | 0 |
| `proof-projection.py` | 124 | 0 | 3 | 0 |
| `proof-projection-3d.py` | 45 | 0 | 1 | 0 |
| `proof-rotate-from-a-to-b.py` | 138 | 0 | 0 | 5 |
| `rotation-from-vectors.py` | 88 | 0 | 0 | 0 (to read) |
| `projection.py`, `projection-rejection-3d.py` | 16 each | — | — | — (still `1 + 1` stubs) |

- An `assert` cell shows nothing in the rendered book. The reader sees code but no result.
- Inline comprehensions such as `[sympy.simplify(sympy.sympify(c)) for c in difference]` put the
  machinery in front of the math.
- `book/docs/conf.py` sets `nb_execution_raise_on_error = True` (and a 600 s timeout). An
  `assert` that fails therefore fails `make docs`. A displayed `[0, 0]` that came out nonzero
  would **not** fail it. See Open question 2.

## Plan (draft; depends on the Open questions)

1. Write the style rule into `tasks/reference/book-outline.md` (next to the structural
   conventions on notebooks), with the Part III cell as the example.
2. Rewrite each notebook in scope, one per commit:
   - a heading per result, worded and labelled as on its page;
   - one check per cell, shown as the cell's output;
   - the `zeros` helper (or the helper chosen in Q2);
   - named operations.
   The math checked stays exactly the same.
3. Gates: `make format` (ty over `book/docs/notebooks`), `tools/check_annotations.py` over the
   notebooks, `make docs`, and a look at the rendered notebook pages in the HTML.

## Open questions

1. **Scope:** are these the notebooks you meant? The table lists `rotate.py`,
   `product-from-projection.py`, `proof-projection.py`, `proof-projection-3d.py`,
   `proof-rotate-from-a-to-b.py` and `rotation-from-vectors.py`, the companions of the Part I
   rotation and projection pages. *(If you meant other pages, name one and I'll rescope.)*
2. **Should a failed check fail the book build?** Today an `assert` fails `make docs`, and a shown
   `[0, 0]` doesn't. One way to keep both: have the `zeros` helper raise when the difference isn't
   zero, and still return the zeros for display. Should it do that? *(Recommend: yes, so the book
   build stays a gate.)*
3. **`symbolically_equal(…)  # -> True` cells** in `proof-rotate-from-a-to-b.py`: convert them to
   `zeros(lhs - rhs)` too, rather than keep `True` as the shown output? *(Recommend: convert, for
   one style throughout.)*
