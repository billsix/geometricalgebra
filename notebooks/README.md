# Notebooks

Every gacalc notebook is in this directory. Open one, change its values, and run it
again, the way you would use a graphing calculator. Start JupyterLab from the repository
root with `make jupyter` (it opens here, at http://127.0.0.1:8888); the files are
percent-format `.py` notebooks, which JupyterLab opens as notebooks.

There are two kinds:

- **Companions.** Each one goes with a page of the book, *Geometry 2*, and computes what
  the page derives, with every coordinate a symbol. Numbers appear only to draw the
  figures, and a cell near the top holds them: change it and rerun to see new pictures.
- **Explorations.** Each one tours a part of the library, with numbers first and symbols
  after. They make up Part IV of the book.

The notebooks that draw figures use ePiX, which the project's container image builds; it
is not on PyPI.

## Part I — The plane

| Notebook | Book page |
| --- | --- |
| `canonical-form.py` | Exact Answers, Not Decimals |
| `one-dimension.py` | One Dimension: m·x + b |
| `vectors-as-number-lines.py` | Vectors as Relative Number Lines |
| `vector-addition.py` | Vector Addition |
| `geometry-from-vectors.py` | Points, Segments, Lines and Polygons from Vectors |
| `rotate.py` | Rotate |
| `proof-rotate-from-a-to-b.py` | Proof: Rotate from the Direction of a to the Direction of b |
| `geometric-product.py` | The Geometric Product |
| `relative-graph-paper.py` | Relative Graph Paper |
| `projection.py` | Projection |
| `proof-projection.py` | Proof: Projection by Rotating to Standard Position |
| `product-from-projection.py` | The Geometric Product from Projection and Rejection |
| `rotation-from-vectors.py` | A Rotation from Two Vectors — No Angle |
| `reflection.py` | Reflection |
| `dual.py` | The Dual |
| `defining-g2.py` | Defining the Algebra: G2 |
| `levels-of-abstraction.py` | Levels of Abstraction |

## Part II — Space

| Notebook | Book page |
| --- | --- |
| `three-dimensions.py` | Into Three Dimensions |
| `projection-rejection-3d.py` | Projection and Rejection in 3D |
| `proof-cross.py` | Proof: The Cross Product by Rotating to Standard Position |
| `proof-projection-3d.py` | Proof: Projection in Space, One Plane at a Time |
| `dual-3d.py` | The Dual in Space |
| `reflection-3d.py` | Reflection in Space |
| `frame-qr-2d.py`, `frame-qr-3d.py` | Frames and QR |
| `proof-reciprocal-frame.py` | Proof: The Reciprocal Frame |

## Part III — The 2D bootstrap

| Notebook | Book page |
| --- | --- |
| `bootstrap-rotation.py` | Step 1: Rotation, from Precalculus |
| `bootstrap-projection.py` | Step 2: Projection, from Rotation |
| `bootstrap-rotation-from-projection.py` | Step 3: Rotation from One Vector to Another, from Projection |
| `bootstrap-product.py` | Step 4: The Geometric Product, from Projection |
| `bootstrap-projection-from-product.py` | Step 5: Projection, through the Product |
| `bootstrap-rotation-from-product.py` | Step 6: Rotation, through the Product |

## Part IV — Explorations

| Notebook | What it explores |
| --- | --- |
| `displaymv.py` | How multiplication works in G_n |
| `displayg2.py` | 𝒢₂: multiplying in the plane |
| `displayg2areas.py` | 𝒢₂: angles and areas |
| `displayg2transforms.py` | 𝒢₂: moving the plane |
| `displaytransforms.py` | Transforms in G_n |
| `displayrotations.py` | Rotations two ways: the versor sandwich vs the projection formula |
| `displaygraded.py` | Graded types — the operation decides the type |
| `displayg3.py` | 𝒢₃: multiplying in space |
| `displayg3measures.py` | 𝒢₃: areas and volumes |
| `displayvectorcalc.py` | Vector calculus in 𝒢₃ — i, j, k and the cross product |
| `displayproofs.py` | Proofs you can check, term by term |
