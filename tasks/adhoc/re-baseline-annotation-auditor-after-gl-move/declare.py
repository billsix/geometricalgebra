"""Insert type declarations above given source lines (bottom-up, by line number).

Usage: python declare.py <file> <spec.json>, spec = [[line, "expected text", ["x: T", ...]], ...].
Each declaration is indented like the target line. The expected text must match the stripped
target line, so a stale line number fails loudly instead of inserting in the wrong place.
Not idempotent by design: run once per file, then delete the spec.
"""

import json
import pathlib
import sys

path: pathlib.Path = pathlib.Path(sys.argv[1])
spec: list[list[object]] = json.loads(pathlib.Path(sys.argv[2]).read_text())
lines: list[str] = path.read_text().splitlines(keepends=True)
entry: list[object]
for entry in sorted(spec, key=lambda e: -int(str(e[0]))):
    number: int = int(str(entry[0]))
    expected: str = str(entry[1])
    declarations: list[str] = [str(d) for d in entry[2]]  # type: ignore[union-attr]
    target: str = lines[number - 1]
    if target.strip() != expected:
        sys.exit(f"{path}:{number}: expected {expected!r}, found {target.strip()!r}")
    indent: str = target[: len(target) - len(target.lstrip())]
    lines[number - 1 : number - 1] = [indent + d + "\n" for d in declarations]
path.write_text("".join(lines))
print(f"{path}: {len(spec)} sites")
