# Emit doc-region markers around every generated class and method

**Status:** in progress — **decided 2026-07-20, hand-written cluster already done.**

**Created:** 2026-07-20
**Part of:** the gacalc-markers effort (was `tasks/emit-doc-region-markers.md`); this is
the generated-modules half. The hand-written half (`functions.py`, `transforms.py`) is
done — see below.

## Decision (Bill, 2026-07-20)

Annotate **all** generated code, but **simply**: one region wrapping each whole class, and
one wrapping each whole method. **Not** the signature/body split used for the hand-written
files — a uniform, mechanical "class + method" pass. Rationale: it is straightforward and
low-risk (a single AST post-pass, no surgical per-member injection), it annotates
everything so the coming white/black-box reassessment has real regions to include, and it
does not require deciding per-method granularity now.

## Naming scheme (descriptive, unique, prefix-free by construction)

- Class region: ``<ClassName> class`` (e.g. ``Vector2 class``, ``G2 class``,
  ``Scalar class``).
- Method region: ``<ClassName> <methodName> method`` (e.g. ``Vector2 __add__ method``).

The trailing ``class`` / ``method`` keyword is load-bearing: it makes the names
**prefix-free**, which is required because Sphinx matches the first line *containing* the
anchor text (so ``Vector2 magnitude`` would otherwise also match
``Vector2 magnitude_squared``). With the suffix, ``Vector2 magnitude method`` is not a
substring of ``Vector2 magnitude_squared method`` (the space+keyword forces divergence).
No SHA1 needed (Bill dropped SHA1); uniqueness is verified with the prefix checker.

## Mechanism — AST post-processing (comments can't live in an AST)

The generator builds `ast` nodes and renders with `ast.unparse`; comments have no AST
node. So (prototyped 2026-07-19):

1. `astbuild.marker(text)` emits `ast.Expr(ast.Constant("@@" + text + "@@"))` — a sentinel
   string-literal statement.
2. `astbuild.inject_region_markers(body)` walks the top-level `ClassDef`s and, for each,
   wraps the class (module-level begin/end siblings) and each method `FunctionDef` in its
   body (class-level begin/end siblings).
3. `astbuild.module_source` renders, then a single regex pass rewrites `'@@...@@'` /
   `"""@@...@@"""` string literals into `# doc-region-... ` comments.

Placement note: a method marker must go *after* any copied docstring (a string literal in
first position becomes the docstring); the wrap inserts the begin-marker before the `def`
(a sibling, not inside), so this is automatic.

## Verification gates

1. `make check-generated` — regenerate twice, byte-identical (determinism).
2. Prefix checker over `src/gacalc/*.py` — 0 collisions, all begin/end balanced.
3. Full suite + `ty` + `ruff` clean.
4. Regenerated `g1/g2/g3/scalar.py` differ from the shipped release *only* by the new
   marker comments.

## What this does NOT mark

Basis-constant assignments (``Cls.e_1 = Cls.from_blade_dict(...)``) are emitted as
module-level statements *after* the class, so they are neither a class nor a method and get
no region in this simple pass. If the book later wants to white-box a "basis" listing, that
is a follow-up. (Flagged to Bill.)

## Hand-written half — DONE 2026-07-20

`functions.py`: `ComposableFunction` (class sig + members), `__call__`, `__matmul__`
(compose), `InvertibleFunction` (class sig + members), `inverse` (sig + body).
`transforms.py`: `translate`, `uniform_scale`, `scale_non_uniform` (each sig + body).
8 regions, 0 prefix collisions, gate green (286 tests, ty + ruff clean).
