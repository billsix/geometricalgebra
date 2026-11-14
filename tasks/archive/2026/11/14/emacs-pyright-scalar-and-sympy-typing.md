# Investigate the type errors Emacs (pyright) reports for reals and sympy times multivectors

**Done:** 2026-11-14. **Created:** 2026-11-10 (William Emerison Six <billsix@gmail.com>).
**Branch:** `sp-e3-axis-and-scalar-typing`. Durable knowledge:
`tasks/reference/pyright-sympy-coefficient-typing.md` (the cause, the measured spellings, and "What
the code does now"); the rule is a `CLAUDE.md` convention bullet.

## Outcome

pyright (the Emacs checker, 1.1.414) no longer reports symbolic coefficients times multivectors as
sympy `Expr`s: 163 of the 166 errors of that cause outside the generated modules are gone, the 3 left
have other roots, and no new pyright error of any kind appeared. Symbolic coefficients are written
`Scalar(s_1) * e_1` (graded modules) or `Gn.from_real(a_1) * e_1` (`Gn`) across `src/`, `tests/` and
`book/docs/notebooks/`, the maintainer's option 1.

## Findings (2026-11-10)

159 of the 195 pyright errors outside the generated modules were one cause (166 by the 2026-11-14
recount, after the standard-position rewrite added a few): sympy's `Expr.__mul__` accepts any right
operand and returns `Expr`, so pyright types `s_1 * e_1` as `Expr` and never consults gacalc's
`__rmul__`; ty types it `Any`. `Scalar(s_1) * e_1` / `Gn.from_real(a_1) * e_1` type correctly under both.

## What changed

- **Discovery and codemod** in `tasks/adhoc/emacs-pyright-scalar-and-sympy-typing/` (removed when
  this task was archived; it is in git history): `discover.sh`
  runs pyright in the image and `extract.py` lists the Expr-cause errors (snapshots
  `data/expr-sites-before.tsv`, 166 rows, and `data/expr-sites-after.tsv`, 3). `wrap_coefficients.py`
  splices `Scalar(` … `)` / `Gn.from_real(` … `)` around the left operand of each `coefficient * blade`
  in a flagged statement, at the AST node's offsets, and adds the `Scalar` import. It wrapped 312
  coefficients; a second run changes nothing.
- **By hand**, the 34 flagged statements the codemod's blade-on-the-right rule could not see:
  scaled multivectors (`Scalar(|a|/|b|) * b`), versors (`Scalar(cos) + Scalar(sin) * Bivector.e_12`),
  the blend `Scalar(cos) * v + Scalar(sin) * v.rotate_90_degrees()`, the frame sums in the tests, and
  `gn.py`'s `sym_vec*` constants. `tests/test_odd3.py` could then annotate `versor: g3.Versor` and
  `conjugated: g3.Odd_3`, and the comment explaining why they had been left inferred went.
- **Docs.** `tasks/reference/pyright-sympy-coefficient-typing.md` › "What the code does now";
  `CLAUDE.md` › "Write a symbolic coefficient through the scalar constructor". No `CHANGELOG.md` entry:
  no public name, value or type changed.

## Decisions

- **Representation-agnostic library bodies put the multivector on the left** (`v * c`,
  `cls.basis_vector(i) * x_i` in `frame.py`, `transforms.py`, `standardposition.py`, and two tests over
  parametrized representations) instead of a scalar constructor. With `cls` a parameter there is no
  safe constructor: `cls.from_real(c)` is the zero vector when `cls` is a graded `Vector`
  (`tasks/graded-scalar-constructors-silent-drop.md`), and `cls.one() * c * v` hides the math. The
  coefficient-times-basis convention is for teaching-facing code, which these bodies are not.
- **`tests/test_operator_typing.py` keeps `t * v`** with a `# pyright: ignore[reportAttributeAccessIssue]`:
  that line tests the runtime operator, which is the point of the test.
- **Not fixed, with reasons** (in the reference doc): `base.symbolic_multivector`'s `typing.Self`
  return (flipping the product moves the error to ty; it is `tasks/typing-base-return-types-redesign.md`'s
  subject), and two `sympy.sympify` results annotated `sympy.Expr` in `transforms.py` (sympy's stubs
  say `Basic`). The generated modules' errors and the 38 other non-generated pyright errors were out of
  scope and are unchanged.

## Verification

- pyright 1.1.414 over `src/gacalc`, `tests`, `notebooks`, `book/docs/notebooks`: Expr-cause errors
  166 → 3; a set diff of every other error before and after shows none new (two in `test_odd3.py`
  gone).
- `make format` (ruff, ty over `src`/`tests`/`tools`/`book/docs/notebooks`, changelog guard): clean.
- `make test`'s pytest run: 1676 passed, 2 skipped. Every changed book notebook ran to completion
  (`frame-qr-2d.py` / `frame-qr-3d.py` in the image, which has ePiX).
