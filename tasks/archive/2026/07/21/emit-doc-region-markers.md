# Emit `doc-region` markers, so modelviewprojection's book can include gacalc source

**Status:** **DONE 2026-07-20 — superseded.** Implemented as two halves, both complete: the
generated-modules half (see companion `annotate-generated-doc-regions.md`, archived
alongside this one) and the hand-written half (`functions.py`/`transforms.py`). Markers are
live and `make check-regions` is green.

**Created:** 2026-07-19
**Requested by:** Bill, 2026-07-19
**Consumer:** modelviewprojection —
`tasks/dangling-book-code-includes.md` in that repo. **25 of its book listings currently
render EMPTY**, 20 of them because the code they teach (`Vector2`, `Vector3`, `translate`,
`uniform_scale`, `InvertibleFunction`, `__add__`, …) moved here, and **gacalc has zero
`doc-region` markers**, so Sphinx has nothing to anchor to.

## Goal

Emit `# doc-region-begin <name>` / `# doc-region-end <name>` comments around the
structural pieces of gacalc's source, so mvp's book can `literalinclude` them. Marker
granularity requested:

- class definitions
- class variables
- instance variables
- **method signatures** (the `def` line)
- **method bodies**

The signature/body split matters because it lets the book publish a method's signature and
body as two adjacent listings **while skipping the docstring in between** — which is how
mvp keeps doctests out of the printed book. Two markers are independent text anchors and
need **not** share a name (mvp relies on this already; `demos/demo03.py` opens
`square viewport` and closes `set to gray`).

## Two halves, very different difficulty

### 1. Hand-written modules — easy, just edit them

Plain comments in the source. Inventory (2026-07-19):

| module | classes | methods | module-level fns |
|---|---|---|---|
| `base.py` | 1 | **61** | 1 |
| `gn.py` | 2 | 5 | 0 |
| `transforms.py` | 0 | 0 | **9** |
| `functions.py` | 4 | 10 | 5 |

`transforms.py` (`translate`, `uniform_scale`, `scale_non_uniform`, the rotation
factories) and `functions.py` (`InvertibleFunction`) are what mvp's ch06 wants most.

### 2. Generated modules — the real design problem

`g1.py` / `g2.py` / `g3.py` / `scalar.py` are **build artifacts**; hand-editing them is
always wrong. Markers must come from `tools/gen_specialized.py`. Volume: g2 4 classes / 97
methods, g3 5 / 122, scalar 1 / 22.

**The blocker: the generator builds `ast` nodes and renders with `ast.unparse`, and
comments cannot exist in a Python AST.** `astbuild.module_source` is a bare
`ast.unparse(...)`; the copyright/import header is the only raw text in the whole pipeline,
for exactly this reason.

## Proposed mechanism — sentinel node + one text pass (PROTOTYPED, WORKS)

Emit each marker as a **bare string-literal expression statement** carrying a sentinel,
then convert sentinels to comments in one regex pass over the unparsed source. `ast.unparse`
indents the statement correctly wherever it sits, so nesting inside classes and methods is
handled for free.

```python
def marker(text):                       # in astbuild
    return ast.Expr(ast.Constant(f"@@{text}@@"))

# after module_source(...):
src = re.sub(r"""^(\s*)(?:'|\"\"\")@@(.*?)@@(?:'|\"\"\")$""", r"\1# \2", src, flags=re.M)
```

Verified output:

```python
def magnitude(self):
    """The magnitude |A|.

Copied from MultiVectorBase."""
    # doc-region-end magnitude signature
    return x
    # doc-region-end magnitude body
```

— re-parses as valid Python, docstring intact, zero sentinels left.

**Caveat that dictates marker placement — a string literal in FIRST position becomes the
docstring.** `ast.unparse` renders it `"""…"""`, and the generator already fills that slot
by copying docstrings from `MultiVectorBase` via `inspect.getdoc`. So a
"method signature" marker must be emitted as the **second** statement, after the
docstring. That is also exactly where the book needs it (the split exists to skip the
docstring), so the constraint and the requirement agree. The regex above matches both
quote styles anyway, as a safety net.

## Naming standard — SHA1 slugs (Bill, 2026-07-19: "I literally don't care about the
names other than them being very highly likely unique")

### Why a hash, and not a hierarchical slug

Marker names are anchors in mvp's `.rst`, so they are a **cross-repo contract**: a rename
silently empties a book listing.

**Sphinx matches the first line *containing* the anchor text, so one anchor being a
*prefix* of another silently selects the wrong region.** Demonstrated with a real Sphinx
build 2026-07-19 — asking for `doc-region-begin gacalc-g2-vector2-magnitude` rendered the
contents of `…-magnitude-signature`, **with no warning**. A hierarchical slug scheme
*reintroduces* the collision it was meant to prevent, since every parent name is a prefix
of its children.

**A fixed-length hex slug cannot be a prefix of another fixed-length hex slug.** The
collision class is eliminated by construction rather than by discipline.

### The standard

**The anchor is a 12-hex SHA1 of the region's IDENTITY, with human-readable text trailing
on the same line:**

```python
# doc-region-begin 2a54c6adf844  gacalc g2 Vector2.magnitude sig
def magnitude(self): ...
# doc-region-end 2a54c6adf844  gacalc g2 Vector2.magnitude sig
```

where the hash is `sha1("gacalc:g2:Vector2.magnitude:sig")[:12]`, over
`<project>:<module>:<qualified-name>:<role>`, roles being
`classdef` / `classvar` / `instancevar` / `sig` / `body`.

**The book anchors on the hash alone; the trailing text is for humans and may be reworded
freely without breaking anything** — verified with a real Sphinx build (`:start-after:
doc-region-begin 3260dee29d77` selected the right region with the descriptive text
present).

**Identity hash, NOT content hash — this is the key choice.** Hashing the region's
*content* would change the anchor on every code edit, breaking the book on every commit.
Hashing its *identity* keeps the anchor stable across edits; it changes only when the thing
is genuinely renamed or moved, which is exactly when the book *should* be forced to look.

### Content SHA1 — a separate job: drift detection

A **content** SHA1 is still valuable, for the different question "did the code inside this
region change?" — the cross-repo drift that a pinned version is supposed to prevent.
Keep it **out of the source** (self-referential, and churns every edit) and in a
**lockfile** in mvp, `anchor -> sha1(region content)`, verified by the anchor checker.
Prototyped over the 12 real regions in mvp's `mathutils.py`; e.g.

```
45989ca00f45   64 lines  define ortho
386ed9fc0889   87 lines  define perspective
```

A changed hash means the printed listing changed — reviewed and re-locked deliberately,
like any lockfile bump.

### The checker still earns its keep

Hashes make collisions vanishingly unlikely, not impossible, and nothing stops a
hand-written marker being mistyped. The checker in
`tasks/dangling-book-code-includes.md` must assert:

1. every anchor referenced by the book **resolves** in its target file;
2. no anchor in a target file is a **prefix** of another (cheap, and catches a hand-rolled
   marker that ignores this standard);
3. each region's **content hash** matches the lockfile.

## Verification

1. **`make check-generated` must still pass** — it regenerates twice and asserts
   byte-identical output. Markers must be deterministic.
2. **Generated output must stay identical to the shipped release, modulo the new markers.**
   Measured 2026-07-19: regenerating locally (sympy 1.14.0, numpy 2.4.6) reproduced the
   PyPI 0.0.10 sdist's `g1/g2/g3/scalar.py` **byte-identical**, even across a numpy version
   difference — so the generator is reproducible in practice and that guarantee is worth
   keeping.
3. **The generator runs `ruff` on its own output** — **TESTED 2026-07-19: safe.** `ruff
   format` preserves every marker comment, unmoved and in order. Its only change is
   inserting a blank line after a class docstring, which is harmless: Sphinx matches an
   anchor by line content, and the region begins after that line either way.
4. Full suite + `ty` + doctests clean.

## Open questions

1. **Marker naming convention?** See Naming — needs deciding before either half starts,
   since mvp's `.rst` anchors must match exactly.
2. **How much to mark?** Marking all 61 `base.py` methods and all 219 generated methods is
   a lot of noise for markers nothing includes yet. Recommend **starting with only what
   mvp's 20 dangling includes actually need** (`translate`, `uniform_scale`,
   `InvertibleFunction`, `Vector2`/`Vector3` class + basis, `__add__`/`__sub__`), then
   widening on demand.
3. **Does the book read gacalc from a git tag or the PyPI sdist?** Open in the consumer
   task. It matters here: the sdist ships **no `tools/`**, so a git checkout is required if
   the book build must regenerate; a git tag ships **no** `g1/g2/g3.py`, so it must
   regenerate. Either way the markers must be *in the generator*, which is what this task
   does.
