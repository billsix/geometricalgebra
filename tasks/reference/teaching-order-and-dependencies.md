# Teaching order and dependencies: build only on what the reader has seen

**Reference document.** States what is true of the book's teaching order and the rule that every
construction uses only results taught before it. Updated in place. The graph of which result
builds on which is `book/docs/proof-dependencies.dot`, drawn on the book's first page
(`book/docs/index.rst`, "How the results build on each other"). The rule was set by William Emerison
Six <billsix@gmail.com>, 2026-11-17, after `notebooks/proof-projection.py` defined its own
rotation from a cosine and a sine instead of using the rotation the book had just built.

## The rule

1. **A construction uses only results taught before it.** In a book page, a notebook, a docstring
   example or a Lean proof that mirrors a chapter, every operation called must come from an earlier
   chapter (or the same chapter, earlier). Check against the graph before choosing a library call.
2. **A library function is judged by how it is built, not by its name.** Several gacalc functions
   compute the same rotation by different routes; only some are available at a given point:
   - `g2.Vector.rotate(θ)`: the rotation by an angle, `proof-rotate` (first).
   - `standardposition.rotation_from_to(from_vector, to_vector)`: the rotation from one direction to
     another, built from the rotation by an angle with cosine and sine read off coordinates
     (`proof-rotate-from-a-to-b`). No general projection, no geometric product. Returns an
     `InvertibleFunction`, so `inverse(R)` is the rotation back.
   - `standardposition.in_plane(rotation, first, second, v)`: one of those 2D rotations applied in a
     coordinate plane of 𝒢₃ (the 3D standard-position constructions).
   - `transforms.projection_rotation(from_vector, to_vector)`: built from general projection onto
     the plane `a ∧ b` **and** the geometric product. Available only after both
     (`product-from-projection`, `rotation-from-vectors`).
   - `transforms.versor_rotation`, `MultiVectorBase.rotor_from_vectors`, `plane_rotation`: built on
     the geometric product and the versor sandwich. Available only from `rotation-from-vectors` on.
3. **Never define a new rotation that takes a cosine and a sine** unless the chapter's subject is
   building a rotation from a cosine and sine without computing an angle. Then say why in the
   notebook and tell the maintainer. The two places this holds today:
   `notebooks/proof-rotate-from-a-to-b.py`'s `rotate_cs` (it builds `rotation_from_to`)
   and the second triangle of `notebooks/bootstrap-rotation-from-projection.py` (Step 3
   builds the rotation from the cosine and sine projection measured).
4. **Part III starts from scratch.** The bootstrap (Steps 1–6) rebuilds the plane: Step 2's
   projection may use only Step 1's rotation by an angle, so its notebooks rotate onto the x-axis
   with `Vector.rotate(-θ)`, `θ = atan2(a_2, a_1)` the angle of `a` (sympy turns
   `cos(atan2(a_2, a_1))` into `a_1 / |a|` itself), not with Part I's `rotation_from_to`.
5. **A comparison may use anything** ("gacalc's projection agrees") as long as the construction
   being checked does not. In the graph that is a dashed arrow.

## The teaching order

From the toctrees in `book/docs/index.rst` and each page's own toctree:

- **Part I, the plane:** … `vector-addition` → `geometry-from-vectors` (a textbook's points,
  segments, rays, lines and polygons from adding and stretching vectors; its angle, perpendicular,
  parallel and area wait for the dot and wedge, in `product-from-projection`'s last section) →
  `rotate` (its proofs: `proof-rotate`, the quarter turn and the rotation
  by an angle; then `proof-rotate-from-a-to-b`, the rotation from one direction to another) →
  `geometric-product` (rotation as multiplication by a rotor) → `rotation-graph-paper` →
  `relative-graph-paper` (a rotation then a translate, read two ways) →
  `projection` (its proof `proof-projection`, built on `rotation_from_to` and the base cases onto
  `e₁`) → `product-from-projection` (the product from projection and rejection; its child page
  `rotation-from-vectors`, the rotor from the product) → `reflection` → `orthogonal` → `dual` →
  `defining-g2` → `levels-of-abstraction` → `interactive-calculator`.
- **Part II, space:** `three-dimensions` → `blade-square-sign` → `projection-rejection-3d` (its
  proofs `proof-projection-3d`, `proof-cross`) → `dual-3d` (the dual of a plane, after `dual`) →
  `reflection-3d` (across a vector and in a plane, after `reflection` and `dual-3d`) →
  `frames-qr` (its proof `proof-reciprocal-frame`).
- **Part III, the 2D bootstrap:** Step 1 rotation → Step 2 projection from rotation → Step 3 rotation
  from one vector to another, from projection → Step 4 product from projection → Step 5 projection
  through the product → Step 6 rotation through the product.

## Keeping the graph true

- `book/docs/proof-dependencies.dot` has one node per named result (projection and rejection
  separately), the second label line naming the page that proves it. A solid arrow `X -> Y` means
  `Y`'s construction uses `X`; a dashed arrow means `Y` is only checked against `X`.
- When a page or notebook adds, removes or changes what a construction calls, update the graph in
  the same change. Hand-written on purpose: it is small enough to read and review (decision 3 of
  `tasks/archive/2026/11/17/book-notebooks-symbolic-proof-style.md`).
- Render it locally with `dot -Tpng book/docs/proof-dependencies.dot -o graph.png`; the book build
  draws it with `sphinx.ext.graphviz` (`book/docs/conf.py`), which needs the `graphviz` package from
  `entrypoint/04-install-docs.sh`.
