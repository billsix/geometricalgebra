# Emit doc-region markers for the generated basis constants (`Cls.e_1 = …`)

**Done 2026-11-04** (branch `mark-basis-constants-for-doc-regions`; agent under William Emerison
Six's batch authorization). Filed 2026-09-08 from modelviewprojection's side as the one residual of
its archived `dangling-book-code-includes.md`.

## What was done

The generator now wraps each class's post-class basis-constant assignments
(`Vector.e_1 = Vector.from_blade_dict(...)`, one per blade) in a **`<Class> basis constants`**
doc-region, one region per class, so modelviewprojection's book can `literalinclude` "here is what
the basis vectors are" (the existing `<Class> cls variables` region covers only the value-less
`ClassVar` *declarations* inside the class body).

- `tools/gen_specialized.py` › `basis_constant_assignments`: emit a `marker(... basis constants)`
  begin/end pair around the assignment block; a class with no nonempty blades (`Scalar`) produces
  no assignments and so **no region** (no empty region).
- `tasks/reference/code-generator-architecture.md` §6 "Emission recap": updated the now-stale line
  that said the basis-constant assignments are "unmarked".
- **Golden-rule shape:** the only tracked diff is `tools/` (+ the reference doc); the regenerated
  `src/gacalc/g*.py` are gitignored, so they change on disk but not in `git status`.

## Decisions (the task's two open questions, both taken on the recommendation)

1. **Exclusion was treated as incidental, not intentional** — nothing in the archive argued for it,
   and the recommendation was to proceed unless the maintainer recalls a reason. (If there was a
   deliberate reason to keep them unmarked, this is the thing to object to at review.)
2. **One region per class**, covering all of that class's constants — what the book wants, and it
   keeps the marker count flat as the dimension grows (𝒢₅ would otherwise add 32 markers per class).

## Verification (direct `podman run` against `gacalc:latest`, 2026-11-04)

Ran the gate's inner commands directly, NOT via `make check-regions`/`make check-generated` — nested,
their `: image` prerequisite re-runs the whole 16 GB `podman build` (the documented gotcha).

- **Markers present, one per class, correct grain:** g2 → G, Vector, Bivector, Versor; g3 → G,
  Vector, Bivector, Trivector, Versor, Odd_3. `Scalar` has none (correct).
- **`tools/check_doc_regions.py`:** "unique, prefix-free, balanced" — green. (`<Class> basis
  constants` collides with / prefixes none of the existing `class` / `declaration` / `cls variables`
  / `instance variables` / `<method> method` names.)
- **Determinism:** regenerated twice, g1/g2/g3 byte-identical — green.

## Follow-up (cross-repo; required for the consumer to benefit — not startable by me now)

modelviewprojection's book can only pick these up through a **published gacalc sdist**. Once gacalc
cuts a release that carries these markers, mvp can restore the two dropped listings (ch05 "vector2d
basis", ch14 "vector3d basis") and bump its pin + its Dockerfile `ARG GACALC_VERSION` together. That
is gated on a gacalc release (the maintainer's step), so it's noted here rather than scaffolded as an
mvp task. mvp's record of the drop: `github.com/billsix/modelviewprojection`
`tasks/archive/2026/09/08/dangling-book-code-includes.md`.

## Related

- `tasks/reference/code-generator-architecture.md` §6 — the doc-region-marker machinery (updated).
