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

"""One-shot codemod for tasks/options-as-enums.md: the call sites and docs.

Rewrites every string spelling of the two library options into its enum:

* ``backend="numpy"`` / ``backend="sympy"`` -> ``backend=MatrixBackend.NUMPY`` /
  ``backend=MatrixBackend.SYMPY``
* ``inverse_method="reciprocal"`` / ``"peel"`` -> ``InverseMethod.RECIPROCAL`` /
  ``InverseMethod.PEEL``

over the files listed below, and adds the import a Python file now needs.  The
definitions themselves (the enums, the signatures, the ``match``) are edited by
hand.  Idempotent: a second run finds nothing to change.
"""

import pathlib
import re

ROOT: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]

REPLACEMENTS: list[tuple[str, str]] = [
    ('backend="numpy"', "backend=MatrixBackend.NUMPY"),
    ('backend="sympy"', "backend=MatrixBackend.SYMPY"),
    ('inverse_method="reciprocal"', "inverse_method=InverseMethod.RECIPROCAL"),
    ('inverse_method="peel"', "inverse_method=InverseMethod.PEEL"),
]

FILES: list[str] = [
    "src/gacalc/functions.py",
    "src/gacalc/transforms.py",
    "src/gacalc/frame.py",
    "tests/test_matrix_template.py",
    "tests/test_transforms.py",
    "tests/test_frame_class.py",
    "book/docs/notebooks/frame-qr-2d.py",
    "book/docs/notebooks/frame-qr-3d.py",
    "tasks/reference/design-decisions.md",
    "tasks/reference/transform-and-composable-function-layer.md",
    "tasks/reference/frames-qr-and-reciprocal-frames.md",
    "CLAUDE.md",
    "README.md",
]

# The import a Python call site needs once it names the enum.
IMPORTS: dict[str, str] = {
    "MatrixBackend": "from gacalc.functions import MatrixBackend\n",
    "InverseMethod": "from gacalc.frame import InverseMethod\n",
}
# Modules that define (or already import) the name themselves.
DEFINES: dict[str, set[str]] = {
    "MatrixBackend": {"src/gacalc/functions.py", "src/gacalc/transforms.py"},
    "InverseMethod": {"src/gacalc/frame.py"},
}


def add_import(text: str, line: str) -> str:
    """Insert ``line`` after the last top-level ``from gacalc`` import."""
    matches: list[re.Match[str]] = list(
        re.finditer(r"^from gacalc\S* import (?:\([^)]*\)|[^\n]*)\n", text, flags=re.M)
    )
    if not matches:
        return line + text
    end: int = matches[-1].end()
    return text[:end] + line + text[end:]


def main() -> None:
    relative: str
    for relative in FILES:
        path: pathlib.Path = ROOT / relative
        if not path.exists():
            continue
        before: str = path.read_text()
        after: str = before
        old: str
        new: str
        for old, new in REPLACEMENTS:
            after = after.replace(old, new)
        if relative.endswith(".py"):
            name: str
            for name, line in IMPORTS.items():
                needs: bool = (
                    f"{name}." in after
                    and relative not in DEFINES[name]
                    and line not in after
                )
                if needs:
                    after = add_import(after, line)
        if after != before:
            path.write_text(after)
            print(f"changed {relative}")


if __name__ == "__main__":
    main()
