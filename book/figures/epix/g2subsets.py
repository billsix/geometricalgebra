# %% [markdown]
# # g2subsets — the kinds of element in 𝒢₂
#
# The whole algebra 𝒢₂ as a box, with the vectors, the versors, and inside the versors
# the scalars and the bivectors. The same diagram is drawn live in
# `book/docs/notebooks/defining-g2.py`. Built with the `epix` Python package.

# %%
from __future__ import annotations

from _venn_scene import (
    BACKGROUND,  # noqa: F401  (read by tools/render_epix_figures.py from the module globals)
    PendingFigure,
    g2_subsets_scene,
)

fig: PendingFigure
with g2_subsets_scene() as fig:
    pass

# %%
fig
