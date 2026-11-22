# Copyright (c) 2025-2026 William Emerison Six
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; version 2.1.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see <https://www.gnu.org/licenses/>.
"""Report where each Lean theorem of ``proofs/GacalcProofs`` is used.

For every ``theorem``/``lemma`` the report counts the mentions of its short name in
the other Lean text and in the reader-facing files (book pages, notebooks, ``src``,
``tests``, ``tools``, the READMEs and ``CLAUDE.md``). A theorem with no mention in
either is a candidate for "stands alone": it may still be a stated result, so read
it before calling it extra. The report also lists a short name declared in more
than one namespace or file.

Limit: names are matched by their last component, so a 𝒢₂ theorem and its 𝒢₃ namesake
count as mentions of each other. The report therefore undercounts unused theorems;
treat a theorem it does not list as unchecked, not as used.

Run from anywhere: ``python tasks/adhoc/lean-proofs-fit-review/lean_usage.py``.
"""

import collections
import pathlib
import re
import subprocess

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]
PROOFS: pathlib.Path = REPO / "proofs" / "GacalcProofs"
READER_FACING: list[str] = [
    "book/docs/*.rst",
    "notebooks/*.py",
    "src",
    "tests",
    "tools",
    "README.md",
    "proofs/README.md",
    "proofs/scripts",
    "CLAUDE.md",
]
DECLARATION: re.Pattern[str] = re.compile(
    r"^(?:@\[[^\]]*\]\s*)?(?:private |protected |noncomputable )*"
    r"(theorem|lemma|def|abbrev|structure|instance)\s+([A-Za-z_][\w.']*)"
)


def declarations(text: str) -> list[tuple[str, str, str]]:
    """The declarations of one Lean file.

    Args:
        text: the file's source.

    Returns:
        One ``(kind, name, namespace)`` per declaration, in file order.
    """
    found: list[tuple[str, str, str]] = []
    namespaces: list[str] = []
    line: str
    for line in text.splitlines():
        opened: re.Match[str] | None = re.match(r"namespace\s+(\S+)", line)
        if opened:
            namespaces.append(opened.group(1))
        closed: re.Match[str] | None = re.match(r"end\s+(\S+)", line)
        if closed and namespaces and namespaces[-1] == closed.group(1):
            namespaces.pop()
        declared: re.Match[str] | None = DECLARATION.match(line)
        if declared:
            found.append((declared.group(1), declared.group(2), ".".join(namespaces)))
    return found


def mentions(short_name: str, text: str) -> int:
    """How many times ``short_name`` appears in ``text`` as a whole identifier.

    Args:
        short_name: the last component of a declaration's name.
        text: the text to search.

    Returns:
        The count, a qualified use (``G2.name``) included.
    """
    whole: re.Pattern[str] = re.compile(
        r"(?<![\w.])(?:\w+\.)*" + re.escape(short_name) + r"(?![\w'])"
    )
    return len(whole.findall(text))


def main() -> None:
    """Print the usage report."""
    sources: dict[str, str] = {
        path.name: path.read_text() for path in sorted(PROOFS.glob("*.lean"))
    }
    all_lean: str = "\n".join(sources.values())
    reader_text: str = subprocess.run(
        ["git", "grep", "-h", "-I", "-e", "", "--", *READER_FACING],
        capture_output=True,
        text=True,
        cwd=REPO,
        check=False,
    ).stdout

    kinds: collections.Counter[str] = collections.Counter()
    homes: dict[str, list[str]] = collections.defaultdict(list)
    lean_only: dict[str, list[str]] = collections.defaultdict(list)
    standalone: dict[str, list[str]] = collections.defaultdict(list)
    cited: int = 0
    file_name: str
    text: str
    for file_name, text in sources.items():
        kind: str
        name: str
        namespace: str
        for kind, name, namespace in declarations(text):
            kinds[kind] += 1
            short_name: str = name.split(".")[-1]
            homes[short_name].append(f"{file_name} ({namespace})")
            if kind not in ("theorem", "lemma"):
                continue
            in_lean: int = mentions(short_name, all_lean) - 1
            in_reader_files: int = mentions(short_name, reader_text)
            if in_reader_files:
                cited += 1
            elif in_lean > 0:
                lean_only[file_name].append(short_name)
            else:
                standalone[file_name].append(short_name)

    print("declarations by kind:", dict(kinds))
    print("theorems cited in a reader-facing file:", cited)
    print(
        "theorems used only by other Lean text:",
        sum(len(names) for names in lean_only.values()),
    )
    print(
        "theorems mentioned nowhere else:",
        sum(len(names) for names in standalone.values()),
    )
    names: list[str]
    print("\n== mentioned nowhere else, by file")
    for file_name, names in sorted(standalone.items()):
        print(f"{file_name} [{len(names)}]: {', '.join(names)}")
    print("\n== short names declared more than once")
    where: list[str]
    for short_name, where in sorted(homes.items()):
        if len(where) > 1:
            print(f"{short_name}: {'; '.join(where)}")


if __name__ == "__main__":
    main()
