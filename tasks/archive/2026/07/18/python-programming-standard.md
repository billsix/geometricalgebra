# Write a Python programming standard (into README.md + CLAUDE.md)

**Created:** 2026-07-18 · **Completed:** 2026-07-18

The maintainer's Python programming standard was written down, put into `CLAUDE.md` with a `README.md`
pointer, ruff's `N` (pep8-naming) family was enabled with all fallout fixed, and the judgment-call
standard was applied across every hand-written module and the generator's emitted output, plus a
`Blade` alias and a typed `TypeSpec`. The repo ended fully ruff + ty clean, 285 tests passing, the
generator deterministic. (The standard has since moved: the portable part to the shared
github.com/billsix/runClaudeInContainer `tasks/reference/python-coding-standard.md`, gacalc's own
specifics to `tasks/reference/python-coding-standard-gacalc.md`.)

The standard was to capture two things: normal Python stated **with its rationale** (why `sorted(xs)`,
an expression returning a new list, rather than `xs.sort()`, which mutates and returns `None`), and the
maintainer's own conventions beyond stock Python (how much to type, inlining single-use values, a
Scheme-influenced function shape).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-07-18)

- **Canonical home = `CLAUDE.md`**; `README.md` gets a short pointer. One source of truth. Rejected:
  README canonical with a CLAUDE.md link, or full text in both (drift).
- **Audience = both, agent-terse**: each rule a statement plus a one-line rationale; a worked
  before/after only where a rule is unusual (the Scheme-style inner function).
- **Inline-single-use is context-dependent**: inline a value used exactly once *unless* the name
  documents an otherwise-opaque expression — lean in library code, named + typed GA values in teaching
  notebooks. Same spirit as the existing "no local aliases" convention.
- **Scheme-style inner function is descriptive/preferred, not enforced.** The model: the main body is a
  nested inner function defined first, with guards/preprocessing/dispatch below it, calling in
  (precedent: `Gn._geometric_product`'s `decrease_grade`, `compose`'s `composed_fn`/`inv_composed_fn`,
  `base.project/reject/reflect`). It is the preferred shape for new code; existing early-return code is
  not churned, and cheap top-of-function `raise`s on nonsensical args stay.
- **Enable ruff `N`** so naming is self-enforcing, handling fallout narrowly rather than dropping
  rules.
- **Organize the standard enforced-vs-prose, maximally**: "(a) ruff enforces these — see `pyproject`
  `select`" once, then spend the words on (b) the judgment calls ruff can't check.
- **Include the full idiom checklist** as one-liners, tagged where ruff enforces them.
- **Annotate types as generously as reasonable**: prefer a declared type over none, including library
  locals; skip only pure noise (`n = 3`); when in doubt, annotate — still bounded by "don't fight the
  checker". This shifted the earlier "locals only when non-obvious" line from
  `tasks/archive/2026/07/18/annotate-local-variable-types.md`.
- **Loop/unpack typing** (the maintainer, 2026-07-18): a statement `for`/unpack target takes a bare
  `name: Type` line above; comprehension loop variables do not (separate scope); a name reused across
  loops of different (sub)types is split into distinctly named typed variables, not left to inference.
- The original questions on length, mechanical enforcement beyond `N`, dedup with CLAUDE.md's scattered
  notes, and further idioms were settled by the shape above: one CLAUDE.md section, existing project
  conventions absorbed by reference.

## Content of the standard (as drafted)

- **(a) Already enforced by ruff**: the `E`/`F`/`I` categories (PEP 8 layout, the Pyflakes tier incl.
  E711/E712/E714/E721/E722, import sorting) plus `TID252 B006 B007 B008 UP007 UP035 S311 S602 T201`,
  and now `N`. The gap before this task was zero naming enforcement.
- **(b) Judgment calls**: naming grammar (PEP 8 cases; verbs for functions, nouns for values;
  `is_`/`has_` predicates; no redundant container suffixes or letter-deleting abbreviations); command–query
  separation and mutate-vs-return (never `x = xs.sort()`, never chain a mutator); type-annotation policy
  (signatures always; read-only params take the covariant `Mapping`/`Sequence`/`Iterable`; polymorphic
  values take `MultiVectorBase`; modern `A | B`); inline-single-use; the inner-function shape; and the
  idiom checklist (EAFP, truthiness for emptiness, `enumerate`/`zip`, simple comprehensions,
  f-strings, `with`, `dict.get`/`defaultdict`, unpacking, `pathlib`, keyword args for meaning,
  consistent returns). Sources: PEP 8, PEP 20, the Google Python Style Guide, ruff's rule docs.
- **House style codified from the existing code**: one concept per file with acyclic layering;
  `match` for structural dispatch; keyword arguments at meaning-bearing call sites; full-word names and
  `n` for the dimension; docstrings citing Hestenes page/equation; frozen-dataclass value types;
  comprehensions and `sum`/`math.prod` with `start=` over accumulation loops; comments explaining why,
  at the point they apply; numeric preservation.

## What was done (rollout, one reviewed increment at a time)

1. **CLAUDE.md** gained "## Coding standard (Python)", organized as above, with the inner-function
   worked example.
2. **README.md** gained a "## Contributing" pointer.
3. **ruff `N` enabled, all fallout fixed with zero suppressions** (the generated `g*.py` were already
   clean): `setup.py` `build_py_with_codegen`→`BuildPyWithCodegen` (N801); `nbplotutils`
   `graphBounds`→`graph_bounds` (N803), `extraLinesMultiplier`→`extra_lines_multiplier: int` (N816);
   generator `SELF`/`COEF`→`self_ann`/`coef_ann` (N806); ~21 uppercase math locals in `test_transforms`
   / `test_graded` lowercased and typed (two `t` collisions → `translate_fn`).
4. **The standard applied to existing code** (the "new code only" default lifted for this task),
   module by module, each gated by `make test` + `make format`:
   - `transforms.py`: untyped locals typed, `typing.Optional[X]` → `X | None`; inner-function shapes
     already idiomatic.
   - `functions.py`: two `Optional` dataclass fields modernized; `compose`/`inverse` locals typed;
     `law` left untyped (verbose type, already commented). Loop variables split per the loop rule
     (`f` → `f` + `invertible_fn`).
   - `base.py`: typing only, zero GA-logic or structure changes (the reference stays pristine).
   - `gn.py`: one typing addition in the blade-canonical recursion, plus the `symbols(...)` unpack as six
     `sympy.Symbol` declarations.
   - `tools/`: (A) the generator source (`gen_specialized.py` + `astbuild.py`), ~89 locals typed with
     ast-node types; skipped a chained assign, `cse` unpacks and param reassigns. (B) the generated
     output made compliant by emitting typed locals (`d: BladeCoef`, `left`/`right: BladeCoef`, cse
     temps `: Coef`), a typed `_coerce`, and ≤88-col coordinate docstrings.
   - **`TypeSpec` hardened** (from the maintainer's type double-check): it was an untyped
     `collections.namedtuple`, so `spec.blades` was `Any` and the blade annotations were only trusted
     gradually. It became a `typing.NamedTuple` (`blades: tuple[Blade, ...]`, …), and `blades_of_grade`'s
     bare `-> tuple` was tightened; ty then verified every blade annotation.
   - **`Blade = tuple[int, ...]`** was introduced in `base.py` beside `Coef` (`BladeCoef =
     dict[Blade, Coef]`), replacing ~40 raw uses across `base.py`, `gn.py`, the generator and
     `test_conformance.py`.
   - `tests/`: ~200 remaining locals typed across all 9 files; 5 ty errors from over-broad
     `MultiVectorBase` (where `.dual()`/`.DIMENSION`/`.coeff_e_1` need the concrete type) and one
     `Coef`-should-be-`Expr` were fixed by narrowing or letting inference give the concrete union. The
     delegated pass first stalled silently, then a synchronous re-run blocked ~27 min with no
     visibility — a lesson to do such passes incrementally.
   - Notebooks: junk names renamed (`asdf*` → `vec_a`/`vec_b`/`biv`, `aoeu*` → `p`/`q`) and typed
     `MultiVector`; the 6 long-standing `displaymv.py` E501 prose lines fixed, making the whole repo
     ruff-clean; pure-scalar scratch locals left untyped per the notebook guidance.

## Verification

After every increment: ruff + ty clean (source and generated), `make check-generated` deterministic,
285 tests passing; all notebooks parsed.
