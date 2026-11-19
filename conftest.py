# Copyright (c) 2025-2026 William Emerison Six
# SPDX-License-Identifier: LGPL-2.1-only
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License, version
# 2.1, as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License (the LICENSE file in this repository)
# for more details.

"""Collection settings shared by the whole test run.

``gacalc.epixscene`` imports ePiX, which the lean image (``MINIMAL_IMAGE=1``, as CI
builds it) leaves out. ``--doctest-modules`` imports every module under ``src``, so
there the package is skipped instead of failing collection.
"""

import importlib.util

collect_ignore_glob: list[str] = (
    [] if importlib.util.find_spec("epix") is not None else ["src/gacalc/epixscene/*"]
)
