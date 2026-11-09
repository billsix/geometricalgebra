#!/usr/bin/env python3
"""Declare each name of a ``a, b = sympy.symbols(...)`` unpack on the lines above.

The house rule (CLAUDE.md, "Coding standard (Python)") types a sympy.symbols
unpack by declaring each name first: ``a_1: sympy.Symbol``.  Rewrites in place
the files named on the command line; idempotent (a name already declared in the
lines directly above is left alone, so a second run changes nothing).

Usage: python tasks/adhoc/annotation-auditor-floor-drift/declare_symbol_unpacks.py FILE...
"""

import pathlib
import re
import sys

UNPACK: re.Pattern[str] = re.compile(
    r"^(\s*)([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)+)\s*=\s*sympy\.symbols\("
)


def rewrite(path: pathlib.Path) -> int:
    """Insert the declarations in one file; return how many were added."""
    lines: list[str] = path.read_text().splitlines(keepends=True)
    out: list[str] = []
    added: int = 0
    line: str
    for line in lines:
        m: re.Match[str] | None = UNPACK.match(line)
        if m is not None:
            indent: str = m.group(1)
            names: list[str] = [n.strip() for n in m.group(2).split(",")]
            # the declarations already directly above this line, if any
            above: set[str] = set()
            k: int = len(out) - 1
            while k >= 0 and re.match(rf"^{indent}\w+: sympy\.Symbol\n$", out[k]):
                above.add(out[k].split(":")[0].strip())
                k -= 1
            n: str
            for n in names:
                if n not in above:
                    out.append(f"{indent}{n}: sympy.Symbol\n")
                    added += 1
        out.append(line)
    path.write_text("".join(out))
    return added


if __name__ == "__main__":
    total: int = sum(rewrite(pathlib.Path(a)) for a in sys.argv[1:])
    print(f"declared {total} names")  # noqa: T201 -- the report is the output
