# Float vs symbolic: how gacalc chooses, and how it should

gacalc runs the same code on Python floats and on sympy expressions. In a few places the two need
different treatment: floats compare with a tolerance, a symbolic result stays exact, and a matrix
comes out as numpy or sympy. This doc covers:
- how each choice is made today;
- the ways Python libraries make such a choice, with sources;
- the recommendation for gacalc.

The research was done in `tasks/archive/2026/11/18/research-numeric-symbolic-mode-threading.md`
(William Emerison Six <billsix@gmail.com> asked for it on 2026-11-16).

## Now: the recommendation is implemented (2026-11-18)

`float_close_to_zero` is `bool | None = None` everywhere it appears:
- `is_orthogonal_to` / `is_parallel_to`;
- `require_on_line`, `coordinate_along` and the four line-to-line and line-to-plane factories;
- `are_linearly_independent` / `is_frame` / `require_frame`;
- the generated `Vector` methods.

`None` is resolved where a comparison happens, by `base.resolve_float_tolerance(flag, values)`.
That uses the caller's `True`/`False`, or else `base.has_float_coefficients(values)`, which treats
any Python `float` or sympy `Float` coefficient as float input. A factory's call-time checks resolve
against the call's input. The record is
`tasks/archive/2026/11/18/tolerance-from-coefficient-type.md`. The inventory below describes the
code as the research found it.

## Before: three mechanisms (as researched)

Counts are from 2026-11-18, made by `git grep` and leaving out the generated `g*.py`. The discovery
script and its output were `tasks/adhoc/research-numeric-symbolic-mode-threading/`, deleted when the
task was archived.

1. **Dispatch on the value's type, with no parameter.** The code looks at what it was given.
   - `MultiVectorBase.exp` picks `math.cos` when `isinstance(θ, float)`, else `sympy.cos`.
   - `magnitude` and `inverse` keep a float a float (`tests/test_numeric_magnitude.py`).
   - In `frame.py`, `_has_float(vectors)` decides whether a frame's internal checks use a
     tolerance (2 sites).
   - The generated 𝒢₂ `rotate` checks `isinstance(angle_in_radians, float)`.
2. **An explicit flag threaded through the calls**, `float_close_to_zero: bool = False`. It
   appears 62 times: `transforms.py` 28, `frame.py` 12, `base.py` 7, `tools/gen_specialized.py` 7,
   tests 8.
   - It starts at `is_orthogonal_to` / `is_parallel_to`.
   - It is passed on by `are_linearly_independent` / `is_frame` / `require_frame`,
     `require_on_line`, `coordinate_along`, the four line-to-line and line-to-plane factories, and
     the generated `Vector` methods.
   - Every layer between the caller and the comparison accepts the flag only to pass it on.
   - Inside its own methods, `frame.py` already replaces the flag with `_has_float`, so it mixes
     mechanisms 1 and 2.
3. **An explicit choice of output representation**, `backend: MatrixBackend = MatrixBackend.NUMPY`.
   It is on `to_matrix` / `to_matrix_template` and has 32 uses, including two book notebooks
   (`frame-qr-2d.py`, `frame-qr-3d.py`). The choice is what to build, not how to compare.

There are also two module-level states, both display-only:
- `base._blade_display_symbols`, a module global set by `set_blade_symbols`, which exists because
  Jupyter calls `_repr_latex_()` with no arguments;
- `nbplotutils._axes`, a `ContextVar` for the axes of the enclosing `with create_graphs():` block.

## The options, and what other libraries do

**(a) Thread an explicit parameter.** gacalc does this today. It is explicit and type-checked, and
a reader sees the choice at the call. The cost is plumbing: every intermediate signature, docstring
and generated method carries a flag it does not use. The flag is also easy to forget, and then a
float input compares exactly and fails on a rounding error.

**(b) A module global** (`set_blade_symbols`-style; galgebra's `Ga.dual_mode(mode)` sets the class
attribute `Ga.dual_mode_value`, which every `dual()` reads, as seen in the local
github.com/pygae/galgebra checkout, `galgebra/ga.py`). It is simple and fits a Jupyter setup cell.
But it is shared by every thread and async task, a test that sets it leaks into the next test, and
a reader cannot see it at the call. SymPy's `global_parameters` (`evaluate`, `distribute`) are its
thread-local cousin. A SymPy maintainer recommends passing `evaluate=False` explicitly and changing
the global flags only once, before any threads start
([sympy mailing list](https://groups.google.com/g/sympy/c/58swQsr7Fn8/m/M1GSVPWyAwAJ)). The SymPy
wiki names the global flag's disadvantage: every object that supports `evaluate=False` must honour
it ([Unevaluated Expressions](https://www.github.com/sympy/sympy/wiki/Unevaluated-Expressions)).

**(c) A dynamically scoped `ContextVar` with a context manager.** Python's form of a Common Lisp
special variable: `with tolerant(): …` makes every call inside the block see the setting, and
leaving the block restores the previous value.
- [PEP 567](https://peps.python.org/pep-0567/) added `contextvars` in Python 3.7. Its motivating
  case is `decimal`'s context, which had been thread-local and broke under concurrent generators
  and async code ([PEP 550](https://peps.python.org/pep-0550/) history;
  [bpo-32630](https://www.python.org/pipermail/python-bugs-list/2018-January/358447.html) moved
  `decimal.localcontext()` onto it).
- NumPy 2.0 made `np.errstate` / `np.printoptions` context-variable based, "fully thread and
  asyncio safe", but not re-entrant and not for decorating async functions
  ([numpy.errstate](https://numpy.org/doc/2.4/reference/generated/numpy.errstate.html),
  [floating point error handling](https://numpy.org/doc/2.4/reference/routines.err.html)).
- `mpmath.workdps(n)` is the same idea for working precision.
- It is the right tool for an *ambient* setting that crosses many layers: precision, error policy,
  print options. gacalc already uses one for the current axes.

**(d) Decide from the values.** Floats get a tolerance and anything else compares exactly, with no
setting at all. This is mechanism 1, which `exp`, `magnitude`, `inverse` and `frame.py` already
use. It is how `math.isclose` versus `==` would be chosen by hand.

## The same call four ways

```python
# (a) today: the flag rides along every layer
f = line_to_line_projection(from_vector=a, to_vector=b, float_close_to_zero=True)
# (b) a global: set once, invisible here
gacalc.set_float_tolerance(True)
f = line_to_line_projection(from_vector=a, to_vector=b)
# (c) a ContextVar: visible as a block
with gacalc.float_tolerance():
    f = line_to_line_projection(from_vector=a, to_vector=b)
# (d) from the values: a and b hold floats, so the checks are tolerant
f = line_to_line_projection(from_vector=a, to_vector=b)
```

**The closure trap in (b) and (c).** A factory returns an `InvertibleFunction` whose body runs
later, when it is called. It checks "is `x` on the line?" at that moment. A setting read when the
body runs gives:

```python
with gacalc.float_tolerance():
    f = line_to_line_projection(
        from_vector=a, to_vector=b
    )  # construction checks: tolerant
y = f(
    x
)  # called outside the block: the on-line check is now exact, and fails on rounding
```

To avoid this, (c) would have to capture the setting when the function is built. That is one more
rule a student reading the code must know. Under (d), the check depends on `x` itself, so it does
the right thing at build time and at call time with no rule to learn.

## Weighed for gacalc

| | (a) thread | (b) global | (c) ContextVar | (d) from values |
| --- | --- | --- | --- | --- |
| Student reads the choice at the call | yes | no | partly (the `with`) | yes: the inputs are floats |
| Plumbing through layers and the generator | heavy | none | none | none |
| Type checkers see it | yes | no | no | yes |
| Test isolation (pytest, doctests) | yes | leaks | yes | yes |
| Jupyter | per call | one cell | a block per cell | nothing to do |
| Closures built now, called later | captured | read late | read late | decided by the input |

## Recommendation

1. **Tolerance: decide from the values (d), and keep the keyword only as an override.**
   - Change `float_close_to_zero: bool = False` to `float_close_to_zero: bool | None = None`.
   - `None` means: tolerant when any coefficient involved is a Python `float`, exact otherwise.
     This is `frame.py`'s existing `_has_float`, moved to `base.py` so every comparison shares it.
   - `True` / `False` force tolerant or exact comparison.
   - Intermediate layers can then stop passing the flag, because the bottom-level comparison sees
     the same values.
   - Symbolic input never changes behaviour: a sympy `Float` inside an expression is not a Python
     `float`, so it stays exact.
   - The change is backwards compatible except for one case: a caller passing floats who relied on
     the exact default. Exact comparison of computed floats is the bug the flag was added to avoid,
     but the change still gets a changelog entry.
2. **Matrix backend: keep the explicit parameter (a).** It chooses the *kind of result*, like
   numpy's `dtype=`. The choice is made at the one call that builds the matrix, not threaded through
   layers, so a hidden setting would gain nothing.
3. **No global and no `ContextVar` for either choice.** Neither choice is ambient state shared by
   many layers once (d) is in place. Both hide the choice from a student reading the call, and both
   fall into the closure trap above. If a session-wide override is ever wanted (for example, "make
   every check exact while debugging"), a `ContextVar` read only where `None` is resolved is the
   form to use, never a plain global. `set_blade_symbols` stays a global because it is display-only
   and Jupyter gives it no other way in.

The implementation is `tasks/tolerance-from-coefficient-type.md` (proposed, needs go-ahead).
