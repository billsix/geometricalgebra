# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: geometricalgebra
#     language: python
#     name: geometricalgebra
# ---

# %%

# Copyright (c) 2025 William Emerison Six
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.


# %%
import warnings

from IPython.display import Math

from geometricalgebra.multivector import (
    MultiVector,
    a_1,
    e_1,
    e_2,
    e_3,
    e_4,
    sym_vec2_1,
    sym_vec2_2,
    sym_vec3_1,
    sym_vec3_2,
)

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %%
# faoeuaoue
i = e_1 * e_2
i

# %%
i * i

# %%
2 * e_1 + 3 * e_2 + 5 * e_1


# %% [markdown]
# Title
# -----
#
# Foo bar

# %%
sym_vec2_1

# %%
sym_vec2_2

# %%
Math("$($" + sym_vec2_1._repr_latex_() + "$)*($" + sym_vec2_2._repr_latex_() + "$)$")

# %%
sym_vec2_1 ^ sym_vec2_2

# %%
e1e2plane = MultiVector.project(onto=e_1 * e_2)
e1e2plane(sym_vec3_1) ^ e1e2plane(sym_vec3_2)

# %%
e2e3plane = MultiVector.project(onto=e_2 * e_3)
e2e3plane(sym_vec3_1) ^ e2e3plane(sym_vec3_2)

# %%
e1e3plane = MultiVector.project(onto=e_1 * e_3)
e1e3plane(sym_vec3_1) ^ e1e3plane(sym_vec3_2)

# %%
# ordering of the plane doesn't matter
e3e1plane = MultiVector.project(onto=e_3 * e_1)
e3e1plane(sym_vec3_1) ^ e1e3plane(sym_vec3_2)

# %%
sym_vec3_1 * sym_vec3_2


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> MultiVector:
    # let gram_fe be e_1
    # let mol_fe be e_2
    unit_gram_fe: MultiVector = e_1
    unit_mol_fe: MultiVector = e_2

    ratio: MultiVector = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)

# %%
for x in MultiVector.bases(1):
    display(Math(x._repr_latex_()))

# %%
MultiVector.symbolic_multivector(grade=1, prefix="a")

# %%
for x in MultiVector.bases(2):
    display(Math(x._repr_latex_()))

# %%
MultiVector.symbolic_multivector(grade=2, prefix="b")

# %%
MultiVector.symbolic_multivector(
    grade=2, prefix="b"
) * MultiVector.symbolic_multivector(grade=2, prefix="d")

# %%
MultiVector.symbolic_multivector(grade=2, prefix="c").r_vector_part(0)

# %%
MultiVector.symbolic_multivector(grade=2, prefix="c").r_vector_part(1)

# %%
MultiVector.symbolic_multivector(grade=2, prefix="c").r_vector_part(2)

# %%
for x in MultiVector.bases(3):
    display(Math(x._repr_latex_()))


# %%
MultiVector.symbolic_multivector(grade=3, prefix="c")


# %%
MultiVector.symbolic_multivector(grade=3, prefix="c").r_vector_part(0)


# %%
MultiVector.symbolic_multivector(grade=3, prefix="c").r_vector_part(1)


# %%
MultiVector.symbolic_multivector(grade=3, prefix="c").r_vector_part(2)


# %%
MultiVector.symbolic_multivector(grade=3, prefix="c").r_vector_part(3)


# %%
a_1 * e_1 * e_2 * e_4

# %%
