# Add symbolic-vector doctests (show the full 2D/3D formula), alongside the numeric ones

**Status:** DONE 2026-08-26 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 4
**Difficulty:** 3

## Outcome (2026-08-26)

Added symbolic-vector doctests **alongside** the numeric ones in `src/gacalc/measure.py`, each showing
the general formula:
- **`signed_area`** → `a_1*b_2 - a_2*b_1` (the clean 2×2 determinant — the showcase);
- **`signed_volume`** → `c_1*(a_2*b_3 - a_3*b_2) - c_2*(a_1*b_3 - a_3*b_1) + c_3*(a_1*b_2 - a_2*b_1)`
  (the 3×3 determinant, cofactor expansion);
- **`area`** and **`content`** → `sqrt((a_1*b_2 - a_2*b_1)**2)` (the magnitude of the determinant).

**Skipped, deliberately:** `volume` (its symbolic output is 94 cols — exceeds the 88 limit, no clean
wrap); `signed_content` (a 2D symbolic case duplicates `signed_area`'s); `content_by_rejection` (per
the decision — its existing concrete `== content` doctest already shows the identity; the raw
symbolic form is unreadable and `simplify` doesn't tame it — covered by
`tests/test_measure.py::test_content_two_ways_both_give_the_determinant_symbolic`).

Outputs captured by running (doctests are exact). **Verified in BOTH host and the container gate**
(the symbolic output matches the container's sympy): ruff + `ty check src` clean, host suite **411**,
and `make test`-parity measure doctests green in the nested `gacalc` image.

## Goal

Keep the existing **concrete numeric** doctests (they read well — you can see the answer), and
**add a second doctest per function that feeds *symbolic* vectors**, so the docstring also shows the
*general formula* the function computes. Bill's model, on `content` (`measure.py:73-80`):

```text
Examples:
    >>> from gacalc.g2 import e_1, e_2
    >>> content([e_1, e_2])          # the unit square
    1
    >>> content([e_1, e_1 + e_2])    # sheared: same base and height
    1
    >>> content([e_1, 2 * e_1])      # dependent -> flat
    0
```

Add, in the same style the code generator uses (symbols `a_1, a_2, b_1, b_2`, matching
`gn.sym_vec2_1 = a_1*e_1 + a_2*e_2` / `sym_vec2_2 = b_1*e_1 + b_2*e_2` in `gn.py:231-234`), a
`(a_1 e_1 + a_2 e_2)`, `(b_1 e_1 + b_2 e_2)` case so the full 2D result is visible:

```text
    >>> import sympy
    >>> a_1, a_2, b_1, b_2 = sympy.symbols("a_1 a_2 b_1 b_2")
    >>> content([a_1 * e_1 + a_2 * e_2, b_1 * e_1 + b_2 * e_2])
    sqrt((a_1*b_2 - a_2*b_1)**2)
```

The reader now sees that the area IS the determinant `a_1 b_2 − a_2 b_1` (here unsigned, `√(det²) =
|det|`). Same idea in 3D where natural.

## What the symbolic results actually are (captured 2026-08-25 — DON'T hand-write these)

Run under the project's pinned sympy and paste the *exact* output; these are what came back today:

| function (2D unless noted) | symbolic result | doctest-worthy? |
| --- | --- | --- |
| `signed_area(v, w)` | `a_1*b_2 - a_2*b_1` | **yes — the clean determinant, ideal** |
| `signed_volume(V, W, U)` (3D) | `c_1*(a_2*b_3 - a_3*b_2) - c_2*(a_1*b_3 - a_3*b_1) + c_3*(a_1*b_2 - a_2*b_1)` | **yes — cofactor expansion, ideal** |
| `content([v, w])` / `area(v, w)` | `sqrt((a_1*b_2 - a_2*b_1)**2)` | yes — legible `|det|` |
| `content([V, W, U])` (3D) | `sqrt((c_1*(a_2*b_3 - a_3*b_2) - c_2*(a_1*b_3 - a_3*b_1) + c_3*(a_1*b_2 - a_2*b_1))**2)` | yes (longer, still legible) |
| `content_by_rejection([v, w])` | `sqrt(a_1**2 + a_2**2)*sqrt(a_1**2*(a_1*b_2 - a_2*b_1)**2/(a_1**2 + a_2**2)**2 + a_2**2*(-a_1*b_2 + a_2*b_1)**2/(a_1**2 + a_2**2)**2)` | **no — ugly, and `sympy.simplify` does NOT clean it up** |

**`content_by_rejection` is the exception** — its raw (lazy, unsimplified) symbolic form is unreadable
and `simplify` leaves it messy. Options (decide when implementing): (a) skip its symbolic doctest;
(b) instead demonstrate the *identity* it exists to teach — that it equals `content` symbolically —
e.g. `>>> sympy.simplify(content_by_rejection([v, w]) - content([v, w])) == 0` → `True` (verify the
exact form that actually returns `True`). Recommend (b): it shows the point without printing noise.

## How (the doctest-exactness rules — these are the whole difficulty)

- **Capture every expected line by RUNNING it, never by hand.** `pytest.ini` sets `addopts =
  --doctest-modules`, so these are *real tests* — the printed sympy expression must match
  byte-for-byte. Generate the algebras (`make generate`) then run each snippet in a REPL and paste
  its output.
- **Build graded symbolic vectors inline** (`from gacalc.g2 import e_1, e_2` + `sympy.symbols`), so
  the input is a precise `Vector` and the example matches the existing concrete one. (Don't reach for
  `gn.sym_vec2_1` — those are the general `Gn`, not the graded type the numeric doctests use.)
- **Reuse the generator's symbol names** `a_1, a_2, b_1, b_2` (and `a_3, b_3, c_1…` in 3D) so the
  symbolic doctests read the same as `gn.py`'s `sym_vec*` and the generator.
- **Verify with `make test`** (runs the doctests) after adding each, and confirm the suite is still
  green.
- **Caveat — sympy-version fragility (note it, accept it):** these doctests pin sympy's *printed*
  form, so a future sympy upgrade that changes term ordering/rendering will break them. That is
  inherent to any sympy doctest and acceptable here; just be aware a sympy bump may require
  re-capturing the expected lines.

## Scope

- **Primary: `src/gacalc/measure.py`** public API — `content`, `area`, `volume`, `signed_area`,
  `signed_volume`, `signed_content`, and `content_by_rejection` (per the exception above). Add the
  symbolic case *after* the existing numeric Examples, not replacing them.
- **Secondary (consider, don't blanket-apply):** other doctested modules — `base.py`, `functions.py`,
  `transforms.py`, `g2.py`, `g3.py` — have doctests too. A symbolic companion helps only where the
  general formula is illuminating (e.g. a product/rotation result); it adds noise where the numeric
  case already says everything. Decide per function; list any you add so review is easy.

## Decisions (Bill, 2026-08-25)

1. **`content_by_rejection`** — show the `== content` identity (option b), not its raw ugly form.
2. **Scope: `measure.py` only** for this task; the `base`/`transforms`/`g2`/`g3` cases are a
   separate follow-up if wanted.

## Cross-links

- `src/gacalc/measure.py` — the docstrings to extend (`content` at line 62, Examples at 73).
- `src/gacalc/gn.py:231-239` — the `a_/b_` symbols and `sym_vec2_*`/`sym_vec3_*` the symbolic style
  mirrors.
- `tasks/reference/content-area-volume.md` — the measures' math (what each formula *should* be).
