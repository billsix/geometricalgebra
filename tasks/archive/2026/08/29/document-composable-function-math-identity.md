# Document the algebraic identity of the composable-function layer (reference doc + docstrings)

**Created:** 2026-08-28 · **Completed:** 2026-08-28
**Source:** the naming/patterns investigation of 2026-08-28

Docs-only (no behaviour change). The durable content lives in
`tasks/reference/composable-function-algebraic-identity.md`; the current-state API map is
`tasks/reference/transform-and-composable-function-layer.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-28)

- **Keep the class names** `ComposableFunction` / `InvertibleFunction`: for a pedagogy project they
  teach more than `Endomorphism`/`Automorphism`. The math names went into docstrings as "also known
  as…", not renames. This settled item 1 ("confirm `ComposableFunction` as the public type name") of
  `tasks/composable-function-followups.md`; its module-name question (`functions` vs `transforms` vs
  `morphisms`) stayed open there.
- **Keep the "Cayley graph" name** in github.com/billsix/modelviewprojection, and document why it is
  defensible rather than renaming it.
- **No code restructuring**: the single type parameter, nominal inheritance, and the overloads all
  stayed (each re-justified below).

## Findings recorded in the reference doc (verified 2026-08-28)

- **Core identity:** `ComposableFunction[V]` is an endomorphism `V → V`; under composition with
  `identity()` they form the endomorphism monoid End(V). `InvertibleFunction[V]` is an automorphism,
  and the subclass relation is literally Aut(V) ⊂ End(V). The only non-invertible ones, `project` /
  `reject`, are idempotent endomorphisms — exactly what linear algebra calls a projection — so
  "projections aren't automorphisms" is a theorem the type split encodes.
- **Secondary structure:** `compose` stores the word in the generators (`components`); `steps()`,
  `latex_repr`, `at()` and `inverse()` (via (g∘h)⁻¹ = h⁻¹∘g⁻¹) are interpretations of that word — the
  free-monoid pattern. `at(t)` has the one-parameter-subgroup shape (`at(0) = id`, `at(1) = f`, and
  inverse commutes with `at`). The `Linearity` lattice LINEAR ⊂ AFFINE ⊂ NONLINEAR mirrors
  GL(V) ⊂ Aff(V) ⊂ bijections, with `max()` as the join.
- **The mvp Cayley graph:** nodes are coordinate spaces, so strictly it is a **Schreier graph** (a
  group acting on a set); but frames form a **torsor** over the transform group (a simply transitive
  action, no privileged frame), and the Schreier graph of a simply transitive action *is* the Cayley
  graph, so the name is honest. Categorically it is a **groupoid**, and `CayleyGraph.path()` computes
  the unique morphism in the free groupoid on the DAG. ROS tf2 is the engineering twin.
- **Why the shape survives review:** one type parameter, not `Morphism[A, B]`, because every actual
  use is `Vector → Vector` of one class (the branded-spaces experiment is parked in
  `tasks/branded-coordinate-space-types.md`); nominal inheritance, not Protocols, because a
  Cayley-graph `Step` requires `InvertibleFunction` (so passing a projection is a type error) and
  there is exactly one implementation. Compared with PyTorch `Transform` (a runtime `bijective` flag),
  TFP `Bijector` (no home for non-invertible maps) and galgebra's `Lt` (no capability split), the
  two-class split is the strongest shape.
- **Known wart, recorded, not fixed:** `InvertibleFunction`'s positional constructor order (`func,
  latex_repr, inverse, latex_repr_inv`) works only because the base's tail fields are `kw_only`, and
  the interleaved `Callable`/`str` pairs are easy to transpose.

The reference doc carries the web references (Wikipedia/Wikibooks on automorphism groups, Starikova
on Cayley graphs, the change-of-basis-groupoid papers, tf2, the Haskell `invertible`/lens `Iso`
precedents, the TFP docs).

## What changed

- Wrote `tasks/reference/composable-function-algebraic-identity.md` (anchors re-verified against the
  tree).
- `src/gacalc/functions.py`: an "Algebraic identity" section in the module docstring, and "Also known
  as" notes on both class docstrings.
- Cross-repo: mvp's `src/modelviewprojection/cayley/cayleygraph.py` module docstring gained an "On the
  name" paragraph (Cayley vs Schreier, the torsor justification, the groupoid and `path()`, tf2, and
  a pointer to this repo's reference doc by GitHub URL).
- Cross-links added in `tasks/reference/transform-and-composable-function-layer.md`,
  `tasks/reference/design-decisions.md` ("Type system & typing"), and
  `tasks/composable-function-followups.md` (item 1 marked settled).

## Verification

Doctests passed (7 in `functions.py`, 2 in mvp `cayleygraph.py`); ruff clean; every edited docstring
RST-validated with docutils. The full containerized gate — `make image` (BUILD_DOCS=1) + `make docs`,
nested — built the book HTML+PDF (exit 0); `gacalc.functions` is autodoc'd (`book/docs/api.rst`), and
the edited docstrings produced zero docutils warnings (the book's 16 warnings were all pre-existing:
`base.py` `|A|`-bar substitution refs and hyperref duplicate labels from the re-exported names). mvp
needed no image build, since its book autodocs only `mathutils`.
