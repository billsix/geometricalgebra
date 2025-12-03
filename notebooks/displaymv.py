# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
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

import geometricalgebra.multivector as mv

# turn warnings into exceptions
warnings.filterwarnings("error", category=RuntimeWarning)

# %%
# faoeuaoue
i = mv.e_1 * mv.e_2
i

# %%
i * i

# %%
2 * mv.e_1 + 3 * mv.e_2


# %% [markdown]
# Title
# -----
#
# Foo bar

# %%
mv.sym_vec2_1

# %%
mv.sym_vec2_2

# %%
mv.sym_vec2_1 * mv.sym_vec2_2


# %%
def gram_fe_to_mol_fe(gram_fe: float) -> mv.MultiVector:
    # let gram_fe be e_1
    # let mol_fe be e_2
    unit_gram_fe: mv.MultiVector = mv.e_1
    unit_mol_fe: mv.MultiVector = mv.e_2

    ratio: mv.MultiVector = (55.85 * unit_gram_fe).inverse() * (1 * unit_mol_fe)
    return gram_fe * unit_gram_fe * ratio


gram_fe_to_mol_fe(gram_fe=95.8)

# %%
