# Hestenes variable-naming notation: Greek scalars, lowercase vectors, CAPITAL multivectors

**What this is:** the durable statement of gacalc's variable-naming convention — the one a reader
infers an element's grade-class from. It is the standard Geometric-Algebra typographic convention
(Hestenes & Sobczyk; MacDonald), applied to Python identifiers. Adopted and swept across the
codebase 2026-10-09 (William Emerison Six <billsix@gmail.com>); the sweep record is
`tasks/archive/2026/10/09/hestenes-notation-variable-naming.md`.

## The rule

| Grade-class of the value the name holds | Style | Examples |
|---|---|---|
| scalar (grade-0 — a plain real / sympy coefficient, an angle) | **Greek letter** (Latin fallback where Greek hurts) | `θ`, `α`, `β`, `λ` / `alpha`, `lambda_` |
| vector (grade-1) | **lowercase Latin** | `a`, `b`, `v`, `x`, `axis` |
| bivector / trivector / pseudoscalar (grade-pure ≥ 2) | **CAPITAL Latin** | `B`, `T`, `I` |
| general / mixed-grade multivector, versor, rotor | **CAPITAL Latin** | `A`, `R`, `M`, `V` |

A reader then tells the grade-class from the name alone, matching the books the library is written
against.

## Scope of the convention

- **Locals and internal (private) helpers only.** Public parameter names are **out of scope** —
  renaming one is a breaking keyword-argument change on the PyPI API (a `v`-tagged SemVer decision,
  not a style pass). So `ruff`'s **N803** (argument naming) stays **ON**; this convention frees only
  local bindings, where **N806 is OFF** (`pyproject.toml [tool.ruff.lint]`).
- **An externally-defined name always wins** (CLAUDE.md "an externally-defined name overrides the
  naming rules"). Never renamed: `cls`, `self`, `n` (the dimension — never `grade`), `m` and `b`
  (the slope/intercept of `f(x) = m*x + b` in `translate`/`uniform_scale`), loop indices `i`/`j`/`k`,
  every dunder, `_repr_latex_`, and the interchange primitives
  `from_blade_dict`/`to_blade_dict`/`_geometric_product`.

## The Greek-scalar caveat (Latin fallback)

Python 3 allows Greek identifiers (PEP 3131), so `θ`/`α`/`λ` are real, valid names — and they pass
the gates (see Tooling below). Use them for **angles** above all (`θ`, `φ`, `α`, `β`), the
unambiguous win. But fall back to a spelled-out or descriptive Latin name where Greek would hurt
more than help, because `λ` collides visually with the `lambda` keyword, Greek is hard to type and
to `grep`, and some editors mangle it:

- a **cos/sin value** has no clean single Greek letter — keep the project's documented `c`/`s`
  spelling (`(cos(θ) = c, sin(θ) = s)`; see CLAUDE.md "Math notation for readers") or a descriptive
  `cos_θ`/`sin_θ`, rather than forcing a cryptic Greek letter;
- a scalar that already has a **clear descriptive name** (`magnitude`, `xy_magnitude`, `area`) is
  already "scalar-ish" — leave it; the intent (grade-0 reads as a scalar name) is what matters, not
  a mechanical letter swap;
- a name **other code must type** as a keyword stays Latin (that is the public-parameter rule above).

The intent is grade-0 → a scalar-ish name; a descriptive Latin scalar name satisfies it as well as a
Greek letter does.

## Tooling facts (verified 2026-10-09)

- Greek identifiers **parse** and pass **`ruff check`**, **`ruff format`**, and **`ty check`** with
  this repo's config. `ruff`'s `select` is `E`/`F`/`I`/`N` plus specific rules; it enables **no
  non-ASCII-name rule** (pylint's `PLC2401` is not selected), so `θ`/`α`/`λ` are accepted.
- `ruff` treats a lowercase Greek letter as lowercase (`"θ".islower()` is `True`), so a Greek name
  satisfies **N803** too — a Greek parameter would not trip argument-naming. (Public parameters are
  still out of scope by the versioning rule above, not by a tooling limit.)

## Sources

The convention "scalars = Greek, vectors = lowercase Latin, general multivectors = uppercase Latin"
is the standard Geometric-Algebra typography. Primary sources the library is written against:
D. Hestenes & G. Sobczyk, *Clifford Algebra to Geometric Calculus*; A. MacDonald, *Linear and
Geometric Algebra*. Summary reference: Wikipedia, "Geometric algebra" — Notation
(<https://en.wikipedia.org/wiki/Geometric_algebra>). PEP 3131 (Python non-ASCII identifiers) is the
feasibility basis for Greek names, not a math source.

## Related

- `tasks/archive/2026/10/05/consider-renaming-scalar-to-real.md` — a separate naming axis (the
  *word* "scalar" vs "real"), orthogonal to this letter-case convention.
- CLAUDE.md "Coding standard (Python)" carries the one-line pointer here; CLAUDE.md "Math notation
  for readers" owns the reader-facing math typography (the `cos(θ) = c` form this doc defers to).
