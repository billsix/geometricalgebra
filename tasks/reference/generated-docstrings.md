# Docstrings on the generated classes (g1/g2/g3)

Durable design record for how the specialized modules (`g1.py`/`g2.py`/`g3.py`, and the
release-only `g4.py`/`g5.py`) get their method docstrings. Read this before changing how
generated docstrings are produced, or before adding/altering the specialized wording.
Author: William Emerison Six <billsix@gmail.com>, 2026-09-26.

Companion: `tasks/reference/code-generator-architecture.md` (how the generator is wired),
`tasks/archive/2026/09/26/generate-missing-docstrings.md` (the task that produced this).

## What is true now

Every method of every generated class carries a docstring:

- The **full class `G`** and the **graded subtypes** (`Scalar`/`Vector`/`Bivector`/
  `Trivector`/`Rotor`/`Odd_3`) each get a docstring on every emitted method.
- For the **dev dimensions g1–g3**, most graded methods carry a **specialized,
  grade-aware** docstring, often with an executable doctest (e.g. `Bivector.reverse`
  documents `B̃ = −B`; `Vector.reverse` documents that reversing a vector is a no-op).
- For methods with **no specialized entry**, and for **all dimensions ≥ 4** (the
  release-only g4/g5, which are niche), the method copies the **generic base docstring**
  from `MultiVectorBase`/`Gn`.
- `@typing.overload` **stubs are left bare** (`...`): overloads never render in autodoc
  (the implementation's docstring is used) and a docstring on a stub is noise.
- **Format: Google / napoleon** (as of 2026-09-26). Both the copied base docstrings and every
  `CUSTOM_METHOD_DOCS` entry / `_*_doc` callable carry the full field set —
  `Args:`/`Returns:`/`Raises:`/`Yields:` with any doctest under an `Example:` header — mirroring
  the hand-written `base.py`/`gn.py`. When adding or editing an entry, keep that shape.
  `Args:` names must match the emitted signature (`rhs`/`other`/`lhs`/`r`/`n`/`blade_coef`/
  `onto`/`away_from`/`across`/`a`,`b`/`from_vector`,`to_vector`/`x`); put a type token in
  `Returns:` only for grade-preserving ops (add/sub/neg/reverse of a closed-grade role) and use
  prose for grade-changing ones (products/`dual`/`exp`) whose type varies by dimension. These
  entries are read as source + run as `--doctest-modules`, NOT autodoc-rendered, so a bare
  re-exported type name in `Returns:` is fine here (unlike `base.py`, where it must be qualified —
  see `book-and-docs-pipeline.md`).

## Why this exists (and what it is NOT for)

`inspect.getdoc` walks the MRO, so a generated override that lacks a literal docstring
**already inherits** the base docstring in rendered autodoc (Sphinx uses `inspect.getdoc`).
So this work is **not** fixing broken rendered docs. Its payoff is:

1. **Grade-specific pedagogy.** The generic base text ("reverse gives grade-r the sign
   (−1)^(r(r−1)/2)") is abstract; a student reading `g2.py`'s `Bivector.reverse` is far
   better served by "a bivector reverses to its negative, `B̃ = −B`". The library is a
   teaching implementation (Hestenes & Sobczyk), and the specialized types g1/g2/g3 are
   where students meet concrete algebras.
2. **Exact, fast doctests** on the specialized types (frozen closed forms), which run under
   `pytest --doctest-modules` — real executable examples per grade.
3. **Self-documenting generated source** — a reader opening `g2.py` sees real docstrings,
   not bare methods relying on MRO lookup.

## The mechanism (`tools/gen_specialized.py`)

All of it lives in the `Method docstrings on the generated classes` section of
`tools/gen_specialized.py`:

- **`CUSTOM_METHOD_DOCS`** — a dict keyed `"<role>|<method>"`, where `role` is a class's
  grade identity (`scalar`/`vector`/`bivector`/`trivector`/`rotor`/`odd`/`full`) or `*`
  (applies to every role). A more specific `role|method` key wins over `*|method`.
- A value (`DocEntry`) is either literal text **or** a `(role, n) -> str` callable, so one
  function can serve a method across every role and emit a **dimension-appropriate**
  example (used for `dual`, the vector wedge/projection/`i`, etc., whose result or validity
  depends on `n`).
- **`custom_method_doc(role, method, n)`** resolves an entry, but only for
  `n in _CUSTOM_DOC_DIMS` (= {1, 2, 3}); otherwise returns `None` (→ generic base copy).
- **`_own_docstring(method)`** is the generic fallback: the docstring `method` actually
  defines on `MultiVectorBase` or `Gn` — deliberately **not** an `object` dunder inherited
  by accident (so generated `__eq__` does not copy "Return self==value.").
- **`inject_method_docstrings(nodes, n, full_name)`** runs once per module in `main()`,
  just before marker injection/rendering. For each class method (skipping overload stubs):
  a custom entry **overrides** whatever the builder emitted; otherwise, if the method has
  no docstring, the generic base docstring is inserted. `doc_expr` handles the 8-space
  method-body indentation so `ast.unparse` renders a clean triple-quoted docstring.

To add or change a specialized docstring: add/edit a `"<role>|<method>"` entry, then
regenerate and verify (below). No other generator code needs to change.

## Conventions the doctests obey (learned the hard way, 2026-09-26)

- **Explicit unit coefficients.** Per the repo's coding standard (`CLAUDE.md`), a bare blade
  that denotes a *coordinate value* is written with an explicit `1 *`: `1 * Vector.e_1`,
  `1 * Bivector.e_12 + 1 * Bivector.e_12 == 2 * Bivector.e_12`. This applies to sum terms,
  product operands, method subjects/arguments, and RHS values. A blade used as a
  **direction** stays bare — the plane args of `Vector.i(Vector.e_1, Vector.e_2)`, the
  `onto` arg of `projected_onto`/`rejected_away_from`, `plane_rotation`/`rotor_from_vectors`
  args, `coefficient(e_1)`.
- **Typed comparisons, never bare numbers.** A multivector result compared with `==` to a
  Python `int` is `False` (`Bivector.e_12 * Bivector.e_12 == -1` is `False`). Compare to the
  correctly-typed value: `... == Scalar.from_scalar(-1)`, `... == Vector.e_3`,
  `... == Rotor.from_scalar(1)`. Methods that return a *coefficient* (`scalar_part`,
  `magnitude_squared`) do return a plain number, so those doctests show the number.
- **Type annotations are for readability, not assertions.** A local in a doctest is
  annotated to *show the reader* the type — `R: Rotor = (1 * Bivector.e_12).exp()` — which
  also teaches that "exp of a bivector is a rotor". Doctests do **not** assert types
  (`type(x).__name__ == '...'`); **type-narrowing is tested in the unit tests** via
  `typing.assert_type` (ty-checked) and runtime `type(...) is ...` — see
  `tests/test_operator_typing.py`, `tests/test_odd3.py`, `tests/test_exp.py`. Those already
  cover the facts the specialized docstrings illustrate (exp→Rotor, odd×odd→Rotor, the
  product/dual grade maps); keep them in sync there, not in doctests.
- **Dimension validity.** A `role|method` entry applies to every dim that role exists in.
  `Vector`/`Scalar` exist in g1 (which has only `e_1` / no plane), so their doctests must be
  g1-valid or the entry must be a `(role, n)` callable that emits a per-`n` example (see
  `_vector_i_doc`, `_vector_proj_doc`, `_vector_rej_doc`, `_vector_dual_doc`,
  `_vector_outer_doc`, `_scalar_dual_doc`, `_bivector_dual_doc`).

## Gotchas

- **Generated files are gitignored**, so `ruff check .` (gitignore-respecting, as
  `entrypoint/format.sh` runs it) does **not** lint them — long docstring lines there are
  not gate failures (the pre-existing property docstrings already run past 88 cols).
- **`tools/gen_specialized.py` is E501-exempt** (`pyproject.toml` `[tool.ruff.lint.per-file-ignores]`):
  its `CUSTOM_METHOD_DOCS` table and doc helpers are mostly docstring-content string
  literals that `ruff format` can't reflow, so E501 is not meaningful for them; the file's
  actual code is still wrapped by `ruff format`. The hand-written `base.py`/`gn.py`
  docstrings are NOT exempt and must stay ≤ 88 cols.
- **Determinism.** `CUSTOM_METHOD_DOCS` is a plain dict and the injection is deterministic,
  so `make check-generated` (regenerate twice, byte-compare) still passes.

## How to verify a change

1. `PYTHONPATH=src python3 tools/gen_specialized.py` (or `make generate`) to regenerate.
2. `PYTHONPATH=src python3 -m pytest --doctest-modules src/gacalc/g1.py src/gacalc/g2.py
   src/gacalc/g3.py` — every added `>>>` must pass.
3. The containerized gate: `make test`, `make check-generated`, `make check-regions`, and
   `make format` (ruff + ty over the hand-written files).
