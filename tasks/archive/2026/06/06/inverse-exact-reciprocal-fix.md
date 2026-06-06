# Fix `inverse()` degrading to floats (exact reciprocal)

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-06

## Symptom

In `notebooks/displayg2.py`, for `m = 3 * e_1 + 4 * e_2` (a `G2` vector):

- `m.normalize()` → `{(1,): 3/5, (2,): 4/5}` — exact fractions ✅
- `m.inverse()`  → `{(1,): 0.12, (2,): 0.16}` — **floats** ❌ (wanted `3/25, 4/25`)

The author wanted the exact (fraction) behavior by default, and recalled deliberately doing something
in `gn.py` to keep `Gn` exact.

## Root cause

It is **not** the generated code or the generator — it is `AbstractMultiVector.inverse()` in
`base.py` (inherited by `G2`):

```python
return self.reverse() * (self.magnitude_squared() ** (-1))
```

For the specialized classes, `magnitude_squared()` is a **raw Python `int`** (here `25`), and in
Python **`int ** -1` returns a `float`** (`25 ** -1 == 0.04`). So the reciprocal — and the whole
inverse — degrades to floats.

Confirmed at the REPL:

```
magnitude_squared(): 25        type: int
25 ** (-1):          0.04      type: float
mag():               5         type: Integer   (sympy)
```

### Why `normalize()` stays exact (the telling contrast)

```python
return self * (abs(self) ** (-1))
```

`abs(self)` → `magnitude()` → `sympy.sqrt(magnitude_squared())`. `sympy.sqrt` always returns a sympy
object (`Integer(5)`), and `Integer(5) ** -1` is an exact `Rational(1, 5)`. `normalize` routes the
`** -1` through a sympy value; `inverse` did not.

### Why `Gn` never showed this (the `gn.py` mechanism the author remembered)

`Gn.__post_init__` **eagerly `sympy.simplify`s every coefficient**, so a `Gn`'s `magnitude_squared()`
is already `sympy.Integer(25)` and `Integer(25) ** -1` → exact `Rational(1, 25)`. The specialized
`G1/G2/G3` deliberately **do not** sympify (the lazy-simplify speed policy), so their coefficients
stay raw Python `int`/`float` — and `int ** -1` falls off the exact path. The eager sympify in
`gn.py` is exactly what was protecting `Gn`.

## The fix (`base.py` `inverse()`)

Route the reciprocal through sympy, the way `normalize` accidentally does:

```python
# sympify the magnitude before the reciprocal: for the specialized
# classes magnitude_squared() is a raw Python int, and ``int ** -1``
# silently degrades to a float -- sympify keeps it exact (Rational).
mag_sq = typing.cast(sympy.Expr, sympy.sympify(self.magnitude_squared()))
return self.reverse() * (mag_sq ** (-1))
```

- **`typing.cast(sympy.Expr, ...)` is required for `ty`.** `sympy.sympify()` is typed to return
  `Basic`, which `ty` doesn't recognize as supporting `**` (`error[unsupported-operator]`). The
  existing exact arithmetic in `cosine`/`normalize` is `ty`-clean because it operates on
  `sympy.Expr`. The cast is a runtime no-op.
- Pulled into a named local (`mag_sq`) so the line stays ≤ 88 chars.
- **Per author request: kept the existing `"Not sure if I'm doing it correctly"` docstring comment.**

### Also fixes `dual()` for free

`dual()` is `self * unit_pseudoscalar(n).inverse()`, so it routed through the same bug. After the fix
`m.dual()` → `{(1,): 4, (2,): -3}` (exact), where it previously degraded to floats too.

## Verification

- `m.inverse()` → `{(1,): 3/25, (2,): 4/25}`; `m.dual()` → `{(1,): 4, (2,): -3}`.
- Genuinely-float inputs still stay numeric (float-in → float-out, just as `sympy.Float`).
- `ty check src`/`tests` clean, `ruff` clean, full suite **161 passing**.

## Performance impact (measured) — small, and not a hot path

| operation | time | note |
| --- | --- | --- |
| `G2.inverse()` (now exact) | **~13.7 µs** | was ~2.8 µs on the old float path → ~5× slower |
| `G2` geometric product `m*m` | ~0.6 µs | the actual hot path; inverse was never near it (~20× slower even pre-fix) |
| `Gn.inverse()` (reference) | ~101 µs | the fixed `G2` is still **~7× faster** than the reference |

**Verdict: not a real problem.** `inverse()` is a *cold* operation (the geometric product is the hot
path); 13.7 µs ≈ 73k inverses/sec; and it remains well under the `Gn` reference.

**The genuine cost is downstream, and it is the point of the change:** the result now carries sympy
`Rational`/`Float` coefficients instead of Python floats, so arithmetic *chained off* an inverse pays
sympy's tax:

| downstream product | time |
| --- | --- |
| using the sympy-`Rational` inverse | ~14.1 µs |
| using a plain-`float` vector | ~4.3 µs |

≈ 3× slower for ops that consume the inverse — inherent to staying exact (sympy numbers are slower
than Python floats everywhere). For the symbolic/exact work this targets, that is correct.

## Escape hatch (not taken; recorded for the future)

The plain fix also sympifies genuinely-float inputs, so a heavy *numeric* pipeline would inherit the
sympy tax on inverse results. If that ever matters, make the sympify **conditional** — only when the
scalar isn't already a Python `float` — to keep float-in → float-out while still fixing the
int/symbolic case. The author chose the simpler exact-always version for now.

## Related

- This is one concrete instance of open-issue #6 (`inverse` carries a "not sure if I'm doing it
  correctly" comment). The comment was **kept** (author's call); the float-degradation aspect is now
  addressed, but the broader "verify against known results" item remains open.
- Boundary respected: fix is in hand-written `base.py` (inherited), **not** generated code — no regen.
