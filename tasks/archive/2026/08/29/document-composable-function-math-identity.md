# Document the algebraic identity of the composable-function layer (reference doc + docstrings)

**Status:** DONE 2026-08-28 — all plan items complete, all gates passed. Ready to archive.
Verified locally (doctests: 7 in `functions.py`, 2 in mvp `cayleygraph.py`; ruff clean; all
edited docstrings RST-validated via docutils) AND via the full containerized gate:
`make image` (BUILD_DOCS=1) + `make docs` (nested, `--cgroups=disabled`) succeeded — the gacalc
book HTML+PDF built (exit 0). `gacalc.functions` IS autodoc'd (`book/docs/api.rst:13`), so the
edited module + class docstrings were actually rendered, and they produced **zero** docutils
warnings/errors. (The book's 16 warnings are all pre-existing and unrelated: `base.py` `|A|`-bar
substitution refs; LaTeX hyperref duplicate-label noise from documenting the re-exported names
under both `gacalc.functions` and `gacalc.transforms`.) mvp needed no image build — its book
autodocs only `mathutils` (`book/docs/api.rst`), so `cayleygraph.py` is not Sphinx-rendered there.
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-08-28 (from the naming/patterns investigation, this session)
**See also:** `tasks/reference/transform-and-composable-function-layer.md` (the current-state API map),
`tasks/composable-function-followups.md` (naming reassessment — partially settled by this task, see
"Decisions already made" below).

## Goal

Two deliverables, docs-only (no behavior change):

1. **A reference doc** — `tasks/reference/composable-function-algebraic-identity.md` — recording
   what `ComposableFunction` / `InvertibleFunction` / the Cayley-graph layer *are* in standard
   mathematical language, with web references, so the design's math identity is durable knowledge
   rather than a conversation.
2. **Docstring additions** citing that identity in the code itself: `src/gacalc/functions.py`
   (module + both classes), and — **cross-repo** — modelviewprojection's
   `src/modelviewprojection/cayley/cayleygraph.py` module docstring.

## Decisions already made (maintainer, 2026-08-28)

- **Keep the existing class names** (`ComposableFunction`, `InvertibleFunction`). For a pedagogy
  project they teach a student more than `Endomorphism`/`Automorphism` would. The math names go in
  docs/docstrings as "this is also known as…", not as renames. (This partially answers
  `tasks/composable-function-followups.md` item 1's "confirm `ComposableFunction` as the public
  type name" — confirmed. The module-name question there, `functions` vs `transforms` vs
  `morphisms`, remains open in that task.)
- **Keep the "Cayley graph" name** in mvp, and *document why it's defensible* (see below) rather
  than renaming to the pedantically-exact term.
- **No code restructuring** — single type parameter, nominal inheritance, and the overloads all
  stay (each was re-justified by the 2026-08-28 investigation; the rationale goes in the reference
  doc).

## Content for the reference doc (the findings, verified 2026-08-28)

All `file:line` anchors below were read directly this session (gacalc `functions.py`, mvp
`cayley/cayleygraph.py`, galgebra `lt.py`).

### The core identity

- `ComposableFunction[V]` (`functions.py:74`) is a self-map `V → V`: an **endomorphism**. The set
  of all of them under composition, with `identity()` (`functions.py:353`) as unit, is the
  **endomorphism monoid** End(V).
- `InvertibleFunction[V]` (`functions.py:187`) is an invertible endomorphism: an **automorphism**.
  The invertibles form the **automorphism group** Aut(V) — the group of units *inside* End(V). The
  subclass relation `InvertibleFunction <: ComposableFunction` is literally "Aut(V) sits inside
  End(V)": the math and the class diagram agree.
- The only bare (non-invertible) `ComposableFunction`s in gacalc are `project` / `reject`
  (`base.py:766`, `base.py:817`). Those are **idempotent endomorphisms** (p∘p = p), and an
  idempotent linear operator is exactly what linear algebra calls *a projection* — so
  "projections aren't automorphisms" is a theorem the type split encodes, not a style choice.
- References: [Automorphism group (Wikipedia)](https://en.m.wikipedia.org/wiki/Automorphism_group);
  [Endomorphism and Automorphism (Wikibooks, Math for Non-Geeks)](https://en.wikibooks.org/wiki/Math_for_Non-Geeks/Endomorphism_and_Automorphism).

### Secondary structures worth recording

- **`compose` stores the word in the generators, not just the product.** `components`
  (`functions.py:95`) keeps the generator sequence; `steps()`, `latex_repr`, `at()`, and
  `inverse()` are each *interpretations* of that word (flatten, typeset, interpolate,
  reverse-and-invert via (g∘h)⁻¹ = h⁻¹∘g⁻¹ at `functions.py:274-278`). This is the standard
  free-structure pattern: elements as words in a generating set, homomorphisms out of the free
  monoid evaluated on demand.
- **`at(t)` is a one-parameter subgroup / flow** (Lie-theory shape t ↦ exp(tX)): `at(0) = id`,
  `at(1) = f`, and the "inverse commutes with at" law (`functions.py:265-268`) enforces that
  interpolation respects the group structure.
- **The `Linearity` lattice is a subgroup chain**: LINEAR ⊂ AFFINE ⊂ NONLINEAR corresponds to
  GL(V) ⊂ Aff(V) ⊂ (all bijections); the `max()` join (`functions.py:320`) says a composite lives
  in the smallest class containing all its parts.

### The Cayley-graph layer (mvp) — why the name is good, and the exact terms

- mvp's graph (`src/modelviewprojection/cayley/cayleygraph.py`) has coordinate **spaces** as nodes
  and per-edge `InvertibleFunction` steps as edges. A textbook **Cayley graph** has *group
  elements* as nodes and one fixed generating set acting at every node
  ([Starikova, Cayley graphs](https://people.maths.bris.ac.uk/~maxmr/Mechanics1/ira.pdf)) — so
  strictly this graph is the generalization: a **Schreier graph** (the graph of a group *acting on
  a set*: nodes = points of the set, edges = generator actions).
- **Why "Cayley graph" is nonetheless defensible:** coordinate frames form a **torsor** over the
  transform group — the group acts *simply transitively* on frames (every frame reachable from
  every other by exactly one transform; no privileged frame, matching the book's
  no-privileged-origin pedagogy). The Schreier graph of a simply transitive action *is* the Cayley
  graph. So the name is honest whenever the frames-as-torsor picture holds, which it does here.
- The categorical name: spaces-as-objects + invertible-transforms-as-arrows is a **groupoid**
  (a category in which every morphism is invertible). `CayleyGraph.path()` — compose along the
  walk, inverting edges walked against their arrow — computes the unique morphism in the **free
  groupoid** on the DAG. Physics models reference-frame changes exactly this way:
  [The Change of Basis Groupoid](https://arxiv.org/pdf/2107.05450),
  [A groupoidal approach to quantum reference frames](https://arxiv.org/html/2608.14133).
- Engineering twin: ROS's [tf2](https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Tf2.html)
  — a tree of coordinate frames whose edges are transforms, with automatic composition and
  inversion along paths. `cayleygraph.py` independently reinvented tf2's core, which is evidence
  the design is sound.

### Design-pattern comparison (why the current shape survives review)

- **One type parameter, not two.** Two parameters (`Morphism[A, B]` — morphism/isomorphism in a
  category) only pay off if coordinate spaces are also branded as distinct static types; every
  actual use in both repos is `Vector → Vector` of one class (e.g. mvp `demo05.py:135-141`), so
  `[A, B]` today would be pure ceremony. (The branded-spaces experiment is parked separately:
  `tasks/branded-coordinate-space-types.md`.) Haskell precedent for the two-parameter shape, for
  the record: [`Control.Category` / the `invertible` package's
  `Bijection a b`](https://hackage.haskell.org/package/invertible) and
  [lens's `Iso`](https://hackage.haskell.org/package/lens/docs/Control-Lens-Iso.html).
- **Nominal inheritance, not Protocols.** The subclass does real work at exactly the boundary the
  docstring names (`functions.py:22-26`): a Cayley-graph `Step` *requires* `InvertibleFunction`,
  making "projection passed where an inverse is needed" a type error, not a runtime surprise.
  Liskov-clean (the subtype only adds capability). Protocols earn their keep with multiple
  independent implementations; there is exactly one, and a Protocol would discard the shared
  machinery (`at`/`steps`/`__matmul__`/`_repr_latex_`).
- **Library comparison:** PyTorch `torch.distributions.Transform` uses a runtime
  `bijective: bool` flag (weaker — `.inv` on a non-bijective transform fails only at runtime);
  TensorFlow Probability [`Bijector`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors)
  requires invertibility of everything, with
  [`Invert`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors/Invert) and
  [`Composition`/`Chain`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors/Composition)
  wrappers mirroring gacalc's `inverse()`/`compose()` — but TFP has no home for non-invertible
  maps at all. gacalc's two-class split is arguably the strongest of the three shapes.
  galgebra's `Lt` (`galgebra/lt.py:161`) has no capability split — `inv()` just fails on singular
  maps.
- **Known wart (record, don't necessarily fix here):** `InvertibleFunction`'s positional
  constructor order (`func, latex_repr, inverse, latex_repr_inv`) works only because the base's
  tail fields are `kw_only` (`functions.py:195-198`) — dataclass-inheritance fragility, and two
  interleaved `Callable`/`str` pairs are easy to transpose silently.

## Plan

- [x] Write `tasks/reference/composable-function-algebraic-identity.md` from the content above
      (all `file:line` anchors re-verified against the working tree, 2026-08-28).
- [x] `src/gacalc/functions.py`: "Algebraic identity" section added to the module docstring;
      "Also known as" notes on both class docstrings (endomorphism/idempotent-projection on the
      base, automorphism/Aut⊂End on the subtype). Doctests still pass (7), ruff clean.
- [x] **Cross-repo:** mvp `cayleygraph.py` module docstring — "On the name" paragraph added
      (Cayley vs Schreier, torsor/simply-transitive justification, groupoid + free-groupoid
      `path()`, tf2 twin, pointer to this repo's reference doc by GitHub URL).
- [x] Cross-links: `transform-and-composable-function-layer.md` Cross-links entry added;
      `design-decisions.md` "Type system & typing" bullet added;
      `composable-function-followups.md` item 1 marked "type names SETTLED" (module-name
      questions there stay open).
- [x] Full containerized book-build gate: gacalc `make image` + `make docs` (nested) succeeded,
      autodoc rendered the edited `functions.py` docstrings with no new warnings (see Status).

## Open questions

(none — decisions recorded above)
