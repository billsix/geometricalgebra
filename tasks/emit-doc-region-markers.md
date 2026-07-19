# Emit `doc-region` markers, so modelviewprojection's book can include gacalc source

**Status:** proposed — **needs a go-ahead.** Design prototyped and verified 2026-07-19;
nothing implemented.

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

## Naming

Marker names become anchors in mvp's `.rst`, so they are a **cross-repo contract** — a
rename silently empties a book listing (that is the bug that created the consumer task).
Needs a convention decided up front, e.g.
`doc-region-begin g2 vector2 class` / `doc-region-end g2 vector2 magnitude signature`.
Must be unique within a file: Sphinx matches the **first** occurrence of the anchor text,
so a marker name that is a prefix of another can silently select the wrong region.

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
