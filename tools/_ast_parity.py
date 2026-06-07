#!/usr/bin/env python
# ruff: noqa: T201
"""Dev-only parity check for the ast-codegen rewrite (delete when done).

Compares the freshly generated src/geometricalgebra/{scalar,g1,g2,g3}.py against a
reference snapshot (the string-generator output) for AST-equivalence:
``ast.dump(ast.parse(ref)) == ast.dump(ast.parse(new))`` per file -- i.e. same
statements/expressions, ignoring formatting and comments. On mismatch it prints a
unified diff of the *normalized* (parse->unparse) sources so the structural
difference is visible.

Usage:  python tools/_ast_parity.py [REF_DIR]   (default REF_DIR=/tmp/ast-ref)
"""

import ast
import difflib
import sys
from pathlib import Path

FILES = ["scalar.py", "g1.py", "g2.py", "g3.py"]
SRC = Path(__file__).parent.parent / "src" / "geometricalgebra"


def normalized(path: Path) -> tuple[str, str]:
    """(ast.dump, normalized source) for a file -- both formatting-independent."""
    tree = ast.parse(path.read_text())
    return ast.dump(tree), ast.unparse(tree)


def main() -> int:
    ref_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/ast-ref")
    failures = 0
    for name in FILES:
        ref_dump, ref_src = normalized(ref_dir / name)
        new_dump, new_src = normalized(SRC / name)
        if ref_dump == new_dump:
            print(f"OK   {name}  (AST-equivalent)")
            continue
        failures += 1
        print(f"FAIL {name}  (AST differs from reference)")
        diff = difflib.unified_diff(
            ref_src.splitlines(),
            new_src.splitlines(),
            fromfile=f"ref/{name}",
            tofile=f"new/{name}",
            lineterm="",
        )
        shown = 0
        for line in diff:
            print("   " + line)
            shown += 1
            if shown > 60:
                print("   ... (diff truncated)")
                break
    print(f"\n{'ALL EQUIVALENT' if not failures else f'{failures} FILE(S) DIFFER'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
