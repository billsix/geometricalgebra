# Emit doc-region markers around every generated class and method

**Created:** 2026-07-20 · **Completed:** 2026-07-20
**Part of:** the gacalc-markers effort (`tasks/archive/2026/07/21/emit-doc-region-markers.md`);
this was the generated-modules half. The hand-written half (`functions.py`, `transforms.py`)
was also done; see the end of this record.

## Outcome

Generated and hand-written doc-region markers were implemented (`astbuild.inject_region_markers`,
`gen_specialized`, `tools/check_doc_regions.py`, `make check-regions`); the gate was green.
Whether to wire `check-regions` into `make test` was deferred as the maintainer's call, outside
this task.

## Decision (William Emerison Six <billsix@gmail.com>, 2026-07-20)

Annotate **all** generated code, but **simply**: one region wrapping each whole class, and
one wrapping each whole method. **Not** the signature/body split used for the hand-written
files, but a uniform, mechanical "class + method" pass. Rationale: it is straightforward and
low-risk (a single AST post-pass, no surgical per-member injection), it annotates
everything so the later white/black-box reassessment has real regions to include, and it
did not require deciding per-method granularity.

## Region kinds (declaration + instance vars added by the maintainer, 2026-07-20)

Per class ``C``: ``C class`` (whole class), ``C declaration`` (the ``class`` line,
ending before the docstring), ``C instance variables`` (the dataclass fields), and
``C <method> method`` per method.

- Property getter/setter share a name, so a setter/deleter takes a qualifier:
  ``Vector2 x method`` (getter) vs ``Vector2 x setter method`` (setter). Any further
  duplicate gets a numeric qualifier, placed *before* ``method`` so names stay
  prefix-free. (This case exposed a gap: an exact-duplicate name is invisible to a
  set-based prefix check; the generated output is verified for exact duplicates too.)
- **Instance vars** are the non-``ClassVar`` ``AnnAssign`` fields (``coeff_*``); the
  ``DIMENSION``/basis ``ClassVar`` declarations are excluded.
- **The declaration END is inserted in TEXT, not the AST.** Putting it before the
  docstring at the AST level bumps the docstring out of first position, and
  ``ast.unparse`` then renders it as an escaped one-liner (ruff does not fix this).
  So ``module_source`` inserts ``# doc-region-end C declaration`` after the ``class C``
  line in the rendered text; docstrings stay triple-quoted (verified for all classes).

The trailing ``class`` / ``method`` keyword makes the names **prefix-free**, which is
required because Sphinx matches the first line *containing* the anchor text (so
``Vector2 magnitude`` would otherwise also match ``Vector2 magnitude_squared``). With the
suffix, ``Vector2 magnitude method`` is not a substring of ``Vector2 magnitude_squared method``.
No SHA1 is used (the maintainer dropped SHA1); uniqueness is verified with the prefix checker.

## Mechanism: AST post-processing (comments can't live in an AST)

The generator builds `ast` nodes and renders with `ast.unparse`; comments have no AST
node. So (prototyped 2026-07-19):

1. `astbuild.marker(text)` emits `ast.Expr(ast.Constant("@@" + text + "@@"))`, a sentinel
   string-literal statement.
2. `astbuild.inject_region_markers(body)` walks the top-level `ClassDef`s and, for each,
   wraps the class (module-level begin/end siblings) and each method `FunctionDef` in its
   body (class-level begin/end siblings).
3. `astbuild.module_source` renders, then a single regex pass rewrites `'@@...@@'` /
   `"""@@...@@"""` string literals into `# doc-region-... ` comments.

A method marker must go *after* any copied docstring (a string literal in first position
becomes the docstring); the wrap inserts the begin-marker before the `def` (a sibling, not
inside), so this is automatic.

## Verification

1. `make check-generated`: regenerating twice was byte-identical (determinism).
2. Prefix checker over `src/gacalc/*.py`: 0 collisions, all begin/end balanced.
3. Full suite + `ty` + `ruff` clean.
4. Regenerated `g1/g2/g3/scalar.py` differed from the shipped release *only* by the new
   marker comments.

## Checkers (both done 2026-07-20)

- **gacalc: new `tools/check_doc_regions.py` + `make check-regions`.** It regenerates, then
  verifies every `src/gacalc/*.py` marker set is (1) free of exact duplicates, (2)
  prefix-free, (3) balanced begin/end, per file and per begin/end kind; exit 1 on any.
  It was verified against all three synthetic failure modes, and the tree passed. It is a host
  target (needs sympy), matching `generate` / `check-generated`.
- **mvp (github.com/billsix/modelviewprojection): `check_doc_regions.py` also catches EXACT
  duplicates**, not just prefixes (it had deduped into a set, which is how the ``x``
  getter/setter dup was nearly missed). The fix also required anchoring the marker regex to the
  **comment form** (`#\s*doc-region-...`): without it the checker matched the `doc-region-begin`
  string inside its *own* regex literals and false-flagged itself. mvp then reported 0
  collisions (the 2 false positives gone), 42 unresolved (unchanged).

Both use the comment-form regex; a bare `doc-region-begin` in a string/docstring does not count.

**Deferred (the maintainer, 2026-07-20; not evaluated): wiring gacalc's `check-regions` into
`make test`** (or the generator's own `test_generator.py`), so marker sanity would be enforced
on every suite run. The maintainer left whether/how undecided. If it ever becomes a dependency
of `make test`, it stops being a directly-invoked target and its `##` help line should go (only
user-invoked targets carry `##`).

## Not marked

Basis-constant assignments (``Cls.e_1 = Cls.from_blade_dict(...)``) are emitted as
module-level statements *after* the class, so they are neither a class nor a method and got
no region in this simple pass. A "basis" listing for the book would be a follow-up (flagged
to the maintainer).

## Hand-written half (done 2026-07-20)

`functions.py`: `ComposableFunction` (class sig + members), `__call__`, `__matmul__`
(compose), `InvertibleFunction` (class sig + members), `inverse` (sig + body).
`transforms.py`: `translate`, `uniform_scale`, `scale_non_uniform` (each sig + body).
8 regions, 0 prefix collisions, gate green (286 tests, ty + ruff clean).
