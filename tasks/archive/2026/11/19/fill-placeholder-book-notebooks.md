# Fill five placeholder book notebooks: defining-g2, dual, one-dimension, reflection, relative-graph-paper

**Status:** done (2026-11-19)
**Created:** 2026-11-19 (William Emerison Six <billsix@gmail.com>)
**Follow-up:** `tasks/fill-remaining-placeholder-book-notebooks.md` (the other five `1 + 1` stubs)

## What this did

Five book notebooks under `book/docs/notebooks/` were 16-line jupytext stubs whose one code cell was
`1 + 1`, and their `.rst` pages held one placeholder sentence. This task filled the five notebooks,
drafted their pages (each marked "Draft … maintainer's voice pass pending"), and added three new
pages that the maintainer's decisions called for. The maintainer gave the direction for each
notebook (William Emerison Six <billsix@gmail.com>, 2026-11-19); the agent filled in the details.

| Page | Notebook | What it teaches |
| --- | --- | --- |
| `dual` | `dual.py` | The dual `a * I⁻¹` is a nonzero vector, and `a · (a I⁻¹) = ⟨(a a) I⁻¹⟩₀ = |a|² ⟨I⁻¹⟩₀ = 0` by associativity and grades, so `cos(θ) = 0`; also the quarter-turn view |
| `dual-3d` (new, Part II) | `dual-3d.py` | With `r = rej_a(b)`, `d = (a ∧ b) I⁻¹ = a r I⁻¹` is perpendicular to `a`, `r` and `b`; it is the cross product |
| `reflection` | `reflection.py` | Reflection across a vector by rotating to standard position, then equal to `proj − rej` and to `b * a * b⁻¹` |
| `reflection-3d` (new, Part II) | `reflection-3d.py` | Across a vector, in a plane `B`, and from the plane's normal `n = B I⁻¹`: the mirror in `B` is minus the reflection across `n` |
| `defining-g2` | `defining-g2.py` | Modelled on `notebooks/displaymv.py`: blades as constants, addition, the three rules, associativity, one example of each kind, the kind of each product, grades, how blades resolve when plotted; opens with a subsets (Venn) diagram |
| `one-dimension` | `one-dimension.py` | `f = translate(b) @ uniform_scale(m)`; graph-paper subsets, then each input `x * e_1` (x = −5..5) beside its output on a parallel number line, stacked so a tilted head sees the line |
| `relative-graph-paper` | `relative-graph-paper.py` | `T_b ∘ S_m` read right to left (standard sheet) and left to right (relative sheet) with `compose_intermediate_fns`; same final sheet; the order of functions matters |
| `rotation-graph-paper` | `rotation-graph-paper.py` (new) | The same two readings for `T_b ∘ R`, R from `rotation_from_to` (45°) |

New ePiX helpers in `book/figures/epix/`: `_venn_scene.py` (the 𝒢₂ subsets diagram, also prebuilt
as the figure `g2subsets.py` for the page), `_line_scene.py` (graph paper and number-line rows),
`_paper_scene.py` (graph paper carried by a function; its `Mapping` is a Protocol so every call
passes keywords, as the `check_epix_keywords` gate requires).

Lean: `proofs/GacalcProofs/Reflect.lean` gained `reflectPlane`,
`reflectPlane_eq_neg_reflectVec_dual` (the mirror in a plane is minus the reflection across its
dual) and the helpers `isVector_dual_of_isBivector`, `normSq_dual_of_isBivector`. The other results
already had Lean twins, cited with `twin:` comments: `dual_perp_dot`, `dual_perp`,
`dual_wedge_perp_left_dot`, `dual_wedge_perp_right_dot`, `reflectVec_eq`. The 2D reflection has no
𝒢₂ Lean theorem, and none was added (the request did not ask for one).

The dependency graph `book/docs/proof-dependencies.dot` gained the four new results, and
`tasks/reference/teaching-order-and-dependencies.md` gained `dual-3d` and `reflection-3d` in Part II.

## Decisions

- **Corrections to the maintainer's sketches** (agreed in conversation 2026-11-19). The 2D dual proof
  needed one step first: the cosine is defined only for two nonzero vectors, so the notebook first
  shows that `a I⁻¹` is a vector of length `|a|`. In 3D the dual of a vector is a plane, so the 3D
  claim is about the dual of `a ∧ rej_a(b)`. "Reflect relative to the plane or relative to its dual,
  and they are equal" holds with a sign: the mirror in `B` is `−(reflection across n)`, because the
  roles of projection and rejection swap; the sandwiches agree, `B v B⁻¹ = n v n⁻¹`.
- **Decision 1 (maintainer, 2026-11-19): the 3D halves go on new Part II pages** `dual-3d` and
  `reflection-3d`, after `projection-rejection-3d`. Reason: the book promises each result uses only
  results before it, and 𝒢₃ is first taught in Part II.
- **Decision 2 (maintainer, 2026-11-19): `relative-graph-paper` uses translate + uniform scale
  only**; the translate+rotate sequences went on `rotation-graph-paper`, which comes after `rotate`.
  Same reason.
- The Venn diagram is ePiX: the book's text-based figure pipeline, rendering to HTML and PDF.
  Graphviz cannot nest regions.
- `one-dimension` comes before vectors are taught, so it calls `e_1` "the direction of the number
  line" and points forward to *Vectors as Number Lines*, as the outline's §B asks.
- In `one-dimension`, the stacked rows run x = −5 at the top to 5 at the bottom, so tilting the
  head to the right turns them into the familiar graph.

## Verification

Each notebook was executed in the `gacalc` image (jupytext → nbconvert) and every check came out 0;
every figure was viewed. `ruff`, `ty check book/docs/notebooks`, `tools/check_notebook_prose_width.py`,
`tools/check_epix_keywords.py` and `tools/check_annotations.py` were clean for the new files.
`proofs/check.sh` passed (1109 declarations on the standard axioms). The book gate (`docs.sh`,
HTML + PDF, every notebook executed) passed in 4.5 min, with no Sphinx or LaTeX warning from the new
pages; it showed that the bold heading font has no 𝒢 glyph, so `defining-g2`'s title uses
`$\mathcal{G}_2$`. The repo-wide `make format` gate ran at the batch's end.
