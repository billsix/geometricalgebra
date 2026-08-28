# The composable-function layer's algebraic identity — what the math calls these things

**Reference document** — the standard mathematical names for what `ComposableFunction` /
`InvertibleFunction` and the Cayley-graph layer *are*, why the project's own names are kept anyway,
and how the design compares to the same shape in other libraries. States what is true; not a task.
Created 2026-08-28 (William Emerison Six <billsix@gmail.com>) from a direct read of
`src/gacalc/functions.py`, modelviewprojection's Cayley layer, and the web references cited inline
(work record: `tasks/archive/.../document-composable-function-math-identity.md` once archived).

Companion docs: `transform-and-composable-function-layer.md` (the API map — *what the surface is*),
`design-decisions.md` (the local rationale). This doc adds the third leg: *what mathematics already
calls this structure*.

## The core identity: endomorphisms and automorphisms

- **`ComposableFunction[V]`** (`src/gacalc/functions.py:74`) is a self-map `V → V`. Mathematics
  calls a structure-preserving self-map an **endomorphism**; the set of all of them under
  composition, with `identity()` (`functions.py:353`) as the unit, is the **endomorphism monoid**
  End(V).
- **`InvertibleFunction[V]`** (`functions.py:187`) is an invertible endomorphism: an
  **automorphism**. The invertibles form the **automorphism group** Aut(V) — the group of units
  *inside* End(V).
- So the subclass relation `InvertibleFunction <: ComposableFunction` is literally
  "Aut(V) sits inside End(V)". The class diagram and the mathematics agree; the inheritance is a
  fact about the objects, not just a code-reuse convenience.
- The only bare (non-invertible) `ComposableFunction`s gacalc constructs are `project` / `reject`
  (`src/gacalc/base.py:766`, `:817`). Both are **idempotent** (p∘p = p), and an idempotent linear
  operator is precisely what linear algebra calls *a projection* — "projections are not
  automorphisms" is a theorem the type split encodes, not a style preference.

References: [Automorphism group — Wikipedia](https://en.m.wikipedia.org/wiki/Automorphism_group);
[Endomorphism and Automorphism — Wikibooks, "Math for Non-Geeks"](https://en.wikibooks.org/wiki/Math_for_Non-Geeks/Endomorphism_and_Automorphism).

### Why the project keeps its own names (decision, 2026-08-28)

`ComposableFunction` and `InvertibleFunction` stay. This is a pedagogy-first codebase: the working
names say what a student can *do* with the value (compose it; invert it), where `Endomorphism` /
`Automorphism` would demand vocabulary before intuition. The math names live here and in the
docstrings as "also known as", so a reader who has the vocabulary snaps the design to it instantly,
and a reader who doesn't loses nothing.

## Secondary structures the code already implements

- **`compose` stores the word, not just the product.** `components` (`functions.py:95`) keeps the
  generator sequence, and `steps()`, `latex_repr`, `at()`, and `inverse()` are each
  *interpretations* of that word: flatten it, typeset it, interpolate it, or reverse-and-invert it
  (the (g∘h)⁻¹ = h⁻¹∘g⁻¹ rule, `functions.py:274-278`). In algebraic terms: elements are
  represented as **words in a generating set**, and each feature is a homomorphism out of the free
  monoid, evaluated on demand. This is why the animation and LaTeX layers fell out so cheaply —
  the free-structure pattern makes new interpretations additive.
- **`at(t)` is a one-parameter subgroup / flow** (the Lie-theory shape t ↦ exp(tX)): `at(0)` is
  the identity, `at(1)` the function, and the "inverse commutes with `at`" law enforced at
  `functions.py:265-273` is exactly the statement that interpolation respects the group structure.
- **The `Linearity` lattice is a subgroup chain.** LINEAR ⊂ AFFINE ⊂ NONLINEAR corresponds to
  GL(V) ⊂ Aff(V) ⊂ (all bijections); the `max()` join (`functions.py:320`) computes the smallest
  class in the chain containing every factor — i.e., which group the composite lives in.

## The Cayley-graph layer (modelviewprojection) — the exact terms, and why the name is fair

The graph lives in [modelviewprojection](https://github.com/billsix/modelviewprojection) at
`src/modelviewprojection/cayley/cayleygraph.py`: nodes are coordinate **spaces**, directed edges
are sequences of `InvertibleFunction` steps, and `CayleyGraph.path()` composes along a walk,
inverting any edge traversed against its arrow.

- **Strictly, that generalizes a Cayley graph.** A textbook **Cayley graph** has *group elements*
  as nodes and one fixed generating set acting at every node
  ([Starikova, *Cayley Graphs*](https://people.maths.bris.ac.uk/~maxmr/Mechanics1/ira.pdf)). A
  graph whose nodes are points of a set a group *acts on*, with edges the generator actions, is a
  **Schreier graph**.
- **Why "Cayley graph" is nonetheless an honest name here:** coordinate frames form a **torsor**
  over the transform group — the group acts *simply transitively* on frames (every frame is
  carried to every other by exactly one transform, and no frame is privileged, matching the book's
  no-privileged-origin pedagogy). The Schreier graph of a simply transitive action **is** the
  Cayley graph. So whenever the frames-as-torsor picture holds — which it does for these scenes —
  the name is correct, not merely close.
- **The categorical name:** spaces-as-objects with invertible-transforms-as-arrows is a
  **groupoid** (a category in which every morphism is invertible), and `path()` computes the
  unique morphism in the **free groupoid** on the DAG. Physics models reference-frame changes the
  same way: [*The Change of Basis Groupoid*](https://arxiv.org/pdf/2107.05450);
  [*A groupoidal approach to quantum reference frames*](https://arxiv.org/html/2608.14133).
- **The engineering twin is ROS's
  [tf2](https://docs.ros.org/en/rolling/Concepts/Intermediate/About-Tf2.html):** a tree of
  coordinate frames whose edges are transforms, with automatic composition and inversion along
  paths. `cayleygraph.py` independently arrived at tf2's core, which is evidence the design is
  sound.

## One parameter, not two — and when two would matter

Two type parameters (`Morphism[A, B]`, invertible case **isomorphism**) is the category-theory
shape; Haskell has it as `Control.Category`, the
[`invertible` package's `Bijection a b`](https://hackage.haskell.org/package/invertible), and
[lens's `Iso`](https://hackage.haskell.org/package/lens/docs/Control-Lens-Iso.html). gacalc stays
single-parameter because **every actual use in both repos is `Vector → Vector` of one concrete
class** (e.g. mvp's demo pipeline paddle→world→NDC annotates `InvertibleFunction[Vector]`
throughout) — `[A, B]` today would be `[Vector, Vector]` ceremony. Two parameters only start
paying rent if coordinate spaces are *also* branded as distinct static types so the checker can
reject cross-space application — that experiment is parked with full costs at
`tasks/branded-coordinate-space-types.md`.

## Nominal inheritance, not Protocols — and the library comparison

- **The subclass does real work at exactly one boundary** (named in the module docstring,
  `functions.py:22-26`): a Cayley-graph `Step` *requires* `InvertibleFunction`, so passing a
  projection where an inverse will be needed is a **type error at the boundary**, not a runtime
  surprise mid-render. Liskov-clean: the subtype only adds capability (an inverse and its label),
  never weakens a base promise.
- **Protocols were considered and declined.** Structural typing earns its keep when multiple
  independent implementations must interoperate without a shared base; here there is exactly one
  implementation, and a Protocol would keep the *interface* while discarding the shared
  *machinery* (`at` / `steps` / `__matmul__` / `_repr_latex_`), forcing it back as mixins.
- **The overload/cast tax is the accepted price.** The `compose` and `__matmul__` overloads and
  the `cast`s in `InvertibleFunction.at` / `inverse` encode "invertible ∘ invertible is
  invertible; anything ∘ non-invertible is not" for the static checker — the cost of expressing a
  capability lattice in Python's type system.
- **How others solved the same problem:**
  - PyTorch `torch.distributions.Transform`: one class with a runtime `bijective: bool` flag —
    weaker; `.inv` on a non-bijective transform fails only at runtime.
  - TensorFlow Probability
    [`Bijector`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors): everything
    must be invertible by contract, with
    [`Invert`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors/Invert) and
    [`Composition`/`Chain`](https://www.tensorflow.org/probability/api_docs/python/tfp/bijectors/Composition)
    wrappers mirroring gacalc's `inverse()` / `compose()` — but with no home for non-invertible
    maps like `project`/`reject` at all.
  - [galgebra](https://github.com/pygae/galgebra)'s `Lt` (`galgebra/lt.py:161`): symbolic linear
    transformation with `__mul__` composition; no capability split — `inv()` simply fails on a
    singular map.

  gacalc's two-class split is the only one of the three that both admits non-invertible maps and
  catches misuse statically.

## Known wart (recorded, deliberately not "fixed")

`InvertibleFunction`'s positional constructor order (`func, latex_repr, inverse, latex_repr_inv`)
works only because the base's tail fields are `kw_only` (`functions.py:195-198`) — a
dataclass-inheritance fragility, and two interleaved `Callable`/`str` pairs are easy to transpose
silently. Keyword construction is the safe idiom; any future constructor change should harden this.
