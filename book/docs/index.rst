..
   Copyright (c) 2026 William Emerison Six

   Permission is granted to copy, distribute and/or modify this document
   under the terms of the GNU Free Documentation License, Version 1.3
   or any later version published by the Free Software Foundation;
   with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

   A copy of the license is available at
   https://www.gnu.org/licenses/fdl-1.3.html.

Geometry 2
==========

The book's two halves follow the plane first and space second. Part I stays in two dimensions:
rotation, the geometric product, projection, reflection, and the algebra behind them. Part II
starts again from the geometric product in three dimensions. Part IV collects the explorations:
notebooks with no page of their own, which you can run and change yourself.

Running the notebooks yourself
------------------------------

Each page that calculates has a companion notebook, shown after the page, and Part IV is
notebooks only. Every one of them runs on your own computer, like a graphing calculator: change
the values and run it again to see the new result and the new pictures. In the book's source
repository (https://github.com/billsix/geometricalgebra), ``make jupyter`` starts JupyterLab
in the ``notebooks/`` directory, which holds every notebook. Its ``README.md`` lists each
notebook with its page.

How the results build on each other
-----------------------------------

Each result is built only from results before it. A solid arrow from one box to another means
the second is built from the first; a dashed arrow means the second is checked against the
first. Part III rebuilds the plane from scratch, so it is its own chain.

.. graphviz:: proof-dependencies.dot

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Part I — The plane

   hook
   canonical-form
   one-dimension
   multiplication
   trigonometry
   sets
   vectors-as-number-lines
   vector-addition
   rotate
   geometric-product
   rotation-graph-paper
   relative-graph-paper
   projection
   product-from-projection
   reflection
   orthogonal
   dual
   defining-g2
   levels-of-abstraction
   interactive-calculator

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Part II — Space

   three-dimensions
   blade-square-sign
   projection-rejection-3d
   dual-3d
   reflection-3d
   frames-qr

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Part III — The 2D Bootstrap

   bootstrap-rotation
   bootstrap-projection
   bootstrap-rotation-from-projection
   bootstrap-product
   bootstrap-projection-from-product
   bootstrap-rotation-from-product

.. toctree::
   :maxdepth: 2
   :numbered:
   :caption: Part IV — Explorations

   notebooks/displaymv
   notebooks/displayg2
   notebooks/displayg2areas
   notebooks/displayg2transforms
   notebooks/displaytransforms
   notebooks/displayrotations
   notebooks/displaygraded
   notebooks/displayg3
   notebooks/displayg3measures
   notebooks/displayvectorcalc
   notebooks/displayproofs

.. toctree::
   :maxdepth: 1
   :caption: Reference

   api
