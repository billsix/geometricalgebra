# Emit doc-region markers for the generated basis constants (`Cls.e_1 = …`)

**Status:** proposed — needs go-ahead. Filed 2026-09-08 from modelviewprojection's side, when
`tasks/dangling-book-code-includes.md` was archived there and this was its one unresolved residual.
**Priority:** 7
**Difficulty:** 2

## BLUF

The generator deliberately does **not** wrap the post-class basis-constant assignments
(`Vector.e_1 = Vector.from_blade_dict(...)`, one per blade, emitted after each class body) in
`doc-region` markers. There *is* a nearby anchor — `<Class> cls variables` — but it covers the
`ClassVar` **declarations**, which carry no values (verified against a generated `g2.py`,
2026-09-08):

```python
    # doc-region-begin Vector cls variables
    DIMENSION: typing.ClassVar[int] = 2
    e_1: typing.ClassVar[Vector]        # <- annotation only; no value
    e_2: typing.ClassVar[Vector]
    # doc-region-end Vector cls variables
...
Vector.e_1 = Vector.from_blade_dict({(1,): 1})   # <- the values, unmarked
Vector.e_2 = Vector.from_blade_dict({(2,): 1})
```

Consequence downstream: **modelviewprojection's book dropped two code listings** — ch05's
"vector2d basis" and ch14's "vector3d basis" — because the only available anchor would have printed
three annotations rather than "here is what `e_1` *is*". The chapters name the constants in prose
instead. Marking the assignments would let those two listings come back on the next gacalc release.

Done = `make check-regions` stays green with a marker set covering the basis constants, and mvp can
point a `literalinclude` at it.

## Context

- **Where the exclusion lives:** `astbuild.inject_region_markers` walks top-level `ClassDef`s and
  marks the class, its declaration, its `cls variables` (the `ClassVar` *declarations*), its instance
  variables, and each method. The basis-constant **assignments** are module-level statements emitted
  *after* the class (a class cannot reference itself mid-definition), so the walk never sees them.
  This is recorded as deliberate in `CLAUDE.md` › "doc-region markers" ("Basis-constant assignments
  (`Cls.e_1 = …`, post-class) are deliberately **not** marked") and in
  `tasks/reference/code-generator-architecture.md` §6.
- **Why it was deliberate:** unknown — the note states the exclusion without a reason, and the two
  archived marker tasks (`tasks/archive/2026/07/21/emit-doc-region-markers.md`,
  `annotate-generated-doc-regions.md`) do not argue it either. It reads as "nothing asked for them",
  not as a decision against. That is the first thing to confirm.
- **The consumer:** modelviewprojection (`github.com/billsix/modelviewprojection`) quotes gacalc's
  source in its book through the PyPI **sdist**, unpacked into `book/docs/_gacalc_src/` at image-build
  time. Its archived record of the drop is
  `tasks/archive/2026/09/08/dangling-book-code-includes.md` ("basis listings dropped rather than
  shown — if a basis listing is wanted back, gacalc would need to mark the basis constants (a future
  release)").

## The naming constraint (this is where the care goes)

`make check-regions` (`tools/check_doc_regions.py`) fails on an exact duplicate, on a name that is a
**prefix** of another in the same file, and on an unbalanced pair. The `cls variables` region already
exists and covers the `ClassVar` *declarations* of the same names, so a new region must not collide
with it and must not prefix it. A name like `Vector basis constants` is free of both today — but
verify per algebra, since `G` / `Vector` / `Bivector` / `Rotor` / `Odd_3` all get constants and the
check is per file.

One region per class (all of that class's assignments in one block) is the natural grain — the book
wants "here are the basis vectors", not one listing per blade. That also keeps the marker count flat
as dimension grows (𝒢₅ would otherwise add 32 markers per class).

## Work

1. Confirm with the maintainer that the exclusion was incidental, not intentional.
2. Emit the markers from the generator — the assignments are built in `generate_class` /
   `generate_graded_type`'s post-class block, so this is a `tools/` change; per the golden rule the
   diff should be `tools/`-only with nothing under `src/gacalc/`.
3. `make check-regions` (it regenerates first) and `make check-generated` (byte-identical twice).
4. Tell mvp the release number so it can restore the two listings and bump its pin + its Dockerfile
   `ARG GACALC_VERSION` together.

## Open questions

1. Was the exclusion deliberate (a reason worth keeping) or just unasked-for? *(Recommend: treat as
   unasked-for unless the maintainer recalls otherwise — nothing in the archive argues for it.)*
2. One region per class covering all its constants, or one per blade? *(Recommend: per class — it is
   what the book wants and it does not scale with dimension.)*
