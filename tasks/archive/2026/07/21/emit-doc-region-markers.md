# Emit `doc-region` markers, so modelviewprojection's book can include gacalc source

**Created:** 2026-07-19 · **Completed:** 2026-07-20
**Requested by:** the maintainer (William Emerison Six <billsix@gmail.com>), 2026-07-19
**Consumer:** modelviewprojection,
github.com/billsix/modelviewprojection `tasks/archive/2026/09/08/dangling-book-code-includes.md`. 25 of its book listings rendered
EMPTY, 20 of them because the code they teach (`Vector2`, `Vector3`, `translate`,
`uniform_scale`, `InvertibleFunction`, `__add__`, …) had moved to gacalc, which had zero
`doc-region` markers for Sphinx to anchor to.

## Outcome

Implemented as two halves, both complete: the generated-modules half
(`tasks/archive/2026/07/21/annotate-generated-doc-regions.md`) and the hand-written half
(`functions.py`/`transforms.py`, recorded in that same doc). The markers went live and
`make check-regions` was green.

> **Superseded:** the SHA1-slug naming standard designed below was dropped by the maintainer
> on 2026-07-20 in favour of readable, prefix-free names with a trailing `class`/`method`
> keyword (`Vector2 magnitude method`). The shipped scheme is in
> `tasks/archive/2026/07/21/annotate-generated-doc-regions.md` and
> `tasks/reference/code-generator-architecture.md`. The SHA1 design is kept here for its
> reasoning about prefix collisions.

## Goal and requested granularity

Emit `# doc-region-begin <name>` / `# doc-region-end <name>` comments around gacalc's source
structure so mvp's book can `literalinclude` them: class definitions, class variables, instance
variables, method signatures and method bodies. The signature/body split lets the book print a
method's signature and body as two adjacent listings **while skipping the docstring between**,
which is how mvp keeps doctests out of the printed book. Begin and end markers are independent
text anchors and need not share a name (mvp's `demos/demo03.py` opens `square viewport` and
closes `set to gray`).

## The two halves

- **Hand-written modules** took plain comments. Inventory (2026-07-19): `base.py` 1 class / 61
  methods / 1 function; `gn.py` 2 / 5 / 0; `transforms.py` 0 / 0 / 9; `functions.py` 4 / 10 / 5.
  `transforms.py` and `functions.py` (`InvertibleFunction`) were what mvp's ch06 wanted most.
- **Generated modules** (`g1/g2/g3/scalar.py`; g2 4 classes / 97 methods, g3 5 / 122, scalar
  1 / 22) are build artifacts, so markers had to come from `tools/gen_specialized.py`. The
  problem: the generator builds `ast` nodes and renders with `ast.unparse`, and comments cannot
  exist in a Python AST.

## Mechanism: sentinel node + one text pass (prototyped, worked)

Each marker is emitted as a bare string-literal expression statement carrying a sentinel
(`ast.Expr(ast.Constant(f"@@{text}@@"))`), and one regex pass over the unparsed source turns
sentinels into comments. `ast.unparse` indents the statement wherever it sits, so nesting inside
classes and methods comes for free. The prototype output re-parsed as valid Python with the
docstring intact and zero sentinels left.

A string literal in FIRST position becomes the docstring (the generator fills that slot by
copying docstrings from `MultiVectorBase` via `inspect.getdoc`), so a signature marker had to be
the second statement, after the docstring. That is also where the book needs it, since the split
exists to skip the docstring. The regex matches both quote styles as a safety net.

## Naming standard as designed: SHA1 slugs (later superseded, see above)

The maintainer, 2026-07-19: "I literally don't care about the names other than them being very
highly likely unique".

- **Marker names are a cross-repo contract**: a rename silently empties a book listing.
- **Sphinx matches the first line *containing* the anchor text**, so an anchor that is a prefix
  of another silently selects the wrong region. A real Sphinx build on 2026-07-19 showed it:
  asking for `doc-region-begin gacalc-g2-vector2-magnitude` rendered the contents of
  `…-magnitude-signature`, with no warning. A hierarchical slug reintroduces exactly this
  collision, since every parent name is a prefix of its children.
- The design: the anchor was a 12-hex SHA1 of the region's **identity**,
  `sha1("<project>:<module>:<qualified-name>:<role>")[:12]` (roles `classdef` / `classvar` /
  `instancevar` / `sig` / `body`), with human-readable text trailing on the same line, e.g. the
  doc-region hash `2a54c6adf844` for `gacalc:g2:Vector2.magnitude:sig`. A fixed-length hex slug
  cannot be a prefix of another. The book would anchor on the hash alone; a real Sphinx build
  with `:start-after: doc-region-begin 3260dee29d77` (a doc-region hash, not a commit) selected
  the right region with the descriptive text present.
- **Identity hash, not content hash**: a content hash would change the anchor on every code edit;
  an identity hash changes only on a rename or move, exactly when the book should be forced to
  look.
- A **content** SHA1 was planned separately for drift detection, kept out of the source in a
  lockfile in mvp (`anchor -> sha1(region content)`). It was prototyped over the 12 real regions
  in mvp's `mathutils.py`; e.g. the doc-region content hashes `45989ca00f45` (64 lines, `define
  ortho`) and `386ed9fc0889` (87 lines, `define perspective`).
- The consumer's anchor checker was to assert that every book anchor resolves, that no anchor is a
  prefix of another, and that each region's content hash matches the lockfile.

## Decisions on the questions this task raised

1. **Naming:** first the SHA1 standard (2026-07-19), then readable `class`/`method`-suffixed names
   (the maintainer, 2026-07-20), which are prefix-free by construction and checked by
   `tools/check_doc_regions.py`.
2. **How much to mark:** the recommendation had been to start with only what mvp's 20 dangling
   includes needed. The maintainer instead chose to annotate **all** generated code with one region
   per class and per method (`tasks/archive/2026/07/21/annotate-generated-doc-regions.md`).
3. **Git tag or PyPI sdist for the book:** left to the consumer task. Either way the markers had to
   be in the generator (the sdist ships no `tools/`; a git tag ships no `g1/g2/g3.py`), which is
   what this task did.

## Verification

1. `make check-generated` (regenerate twice, byte-identical) still passed; markers are
   deterministic.
2. Regenerating locally (sympy 1.14.0, numpy 2.4.6) reproduced the PyPI 0.0.10 sdist's
   `g1/g2/g3/scalar.py` byte-identical, even across a numpy version difference, so output stays
   identical to the shipped release modulo the markers.
3. `ruff format` on the generator output preserved every marker comment, unmoved and in order;
   its only change was a blank line after a class docstring, which is harmless because Sphinx
   matches anchors by line content.
4. Full suite + `ty` + doctests clean.
