#!/usr/bin/env python3
"""Codemod for tasks/math-notation-parens-star-named-angles: the MECHANICAL part of the three
notation rules (parentheses apply, `*` multiplies, every angle is named), matched on CONTENT.

Applied only where a reader sees math, never to code:

* ``.py``  -- comment tokens and string tokens (docstrings, the generator's docstring table,
  figure label strings, notebook markdown cells), skipping doctest lines (``>>>``/``...``);
* ``.lean`` -- comment spans only (``/-- … -/``, ``/-! … -/``, ``-- …``); Lean code is exempt;
  in those spans the star carries no surrounding spaces (``|a|*|b|``, ``R*v*R̃``);
* ``.rst`` / ``.md`` -- whole file, except ``blade-square-sign.rst`` (its sliding diagrams are
  hand-edited: a ``*`` between every neighbour would break their column alignment), and except
  text between ``<!-- notation-rule: begin -->`` / ``<!-- notation-rule: end -->`` markers,
  which is where a doc QUOTES the rejected spellings on purpose.

What it rewrites (every rule is a plain regex; read the diff -- judgment calls are hand edits):

* rule 1: ``\\cos\\theta`` -> ``\\cos(\\theta)``, ``\\sin^2\\theta`` -> ``\\sin^2(\\theta)``,
  ``cos θ`` -> ``cos(θ)``, ``cos (θ / 2)`` -> ``cos(θ / 2)`` (only when the parenthesis opens
  on an angle or a magnitude), ``cos|B|`` -> ``cos(|B|)``;
* rule 3 (only the forms whose angle is unambiguously θ): ``cos² + sin² = 1`` ->
  ``cos²(θ) + sin²(θ) = 1``, ``(cos = c, sin = s)`` -> ``(cos(θ) = c, sin(θ) = s)``,
  ``cos = 0`` -> ``cos(θ) = 0``, ``cos = (…`` -> ``cos(θ) = (…``; the book pages' ``\\cos = …``
  (whose angle is ``-\\theta``, ``-\\beta``, …) are hand edits;
* rule 2: magnitudes side by side (``|a||b|``, ``|a| |b|``, ``|a|\\,|b|``, ``|a|^2|b|^2``) get
  ``*``; a magnitude, a trig value, a coordinate, a coefficient, a digit, ``θ``, ``r``, ``I``,
  ``x``/``y`` or a closing parenthesis followed by a basis vector, a parenthesis, ``\\vec``, a
  trig value or a ``\\begin{bmatrix}`` gets ``*``; the middle dot used as SCALAR times (left
  operand a scalar) becomes ``*`` -- a middle dot between two vectors (``a·b``, the dot
  product) is left alone; the sandwich ``R v R̃`` / ``R v R⁻¹`` / ``R̃ v R`` / ``R R̃`` ->
  ``R * v * R̃`` …; ``(v e₁₂)`` -> ``(v * e₁₂)``; ``e₁e₂`` -> ``e₁ * e₂``; ``e_1 e_2 … e_r`` ->
  ``e_1 * e_2 * … * e_r``.

Idempotent: a second run changes nothing. Repo-relative paths (the repo root is three
directories above this file). Run from anywhere::

    python tasks/adhoc/math-notation-parens-star-named-angles/fix.py
"""

from __future__ import annotations

import io
import pathlib
import re
import sys
import tokenize
from collections.abc import Callable

REPO: pathlib.Path = pathlib.Path(__file__).resolve().parents[3]

Rule = tuple[re.Pattern[str], str | Callable[[re.Match[str]], str]]

ANGLES_TEX = r"(theta|beta|alpha|phi|varphi|psi)"
ANGLES_UNI = "θβαφψ"
TRIG_TEX = r"\\(?:cos|sin|tan)(?:\^2)?\([^()]*\)"  # \cos(\theta) , \sin^2(\theta_1)
TRIG_UNI = r"(?:cos|sin|tan)²?\([^()]*\)"  # cos(θ) , sin²(θ/2)
MAG = r"\|[^|\s]{1,14}\|(?:\^2|²)?"  # |a|  |\vec{a}|  |f∧t|  |a|^2  |a|²

RULE1: list[Rule] = [
    (
        re.compile(
            r"\\(cos|sin|tan)(\^2|\^\{2\})? *\\"
            + ANGLES_TEX
            + r"(_\{[^}]*\}|_[0-9a-zA-Z])?"
        ),
        lambda m: f"\\{m.group(1)}{m.group(2) or ''}(\\{m.group(3)}{m.group(4) or ''})",
    ),
    (
        re.compile(r"\b(cos|sin|tan)(²)? ?([" + ANGLES_UNI + r"][₀-₉0-9]?)\b"),
        lambda m: f"{m.group(1)}{m.group(2) or ''}({m.group(3)})",
    ),
    # cos (θ / 2) , sin (β − α) , cos (|B|)  ->  cos(θ / 2) …  (never `sin (§3)`)
    (
        re.compile(r"\b(cos|sin|tan)(²)? \((?=[" + ANGLES_UNI + r"|(0-9−-])"),
        lambda m: f"{m.group(1)}{m.group(2) or ''}(",
    ),
    (re.compile(r"\b(cos|sin)\|([^|]+)\|"), lambda m: f"{m.group(1)}(|{m.group(2)}|)"),
]

RULE3: list[Rule] = [
    (re.compile(r"cos² ?\+ ?sin² ?= ?1"), "cos²(θ) + sin²(θ) = 1"),
    (re.compile(r"\(cos = c, sin = s\)"), "(cos(θ) = c, sin(θ) = s)"),
    (
        re.compile(r"\b(cos|sin) = (0|-1|\()"),
        lambda m: f"{m.group(1)}(θ) = {m.group(2)}",
    ),
]

RULE2: list[Rule] = [
    # magnitude followed by: a magnitude, a trig value, a parenthesis, a basis vector  ->  *
    (re.compile(r"(" + MAG + r")(?:\\,| )?(?=" + MAG + r")"), r"\1 * "),
    (re.compile(r"(" + MAG + r")(?:\\,| )?(?=\\?(?:cos|sin)²?(?:\^2)?\()"), r"\1 * "),
    (
        re.compile(
            r"(" + MAG + r")(?:\\,)?(?= ?\( ?(?:\||[a-z] |[0-9]+ ?[*/+]|\\|-|−))"
        ),
        r"\1 * ",
    ),
    (re.compile(r"(" + MAG + r")(?:\\,| )?(?=e_[0-9]|e[₀-₉])"), r"\1 * "),
    # digit before a magnitude or a (e_ … parenthesis  ->  *
    (re.compile(r"(?<![-−\w])([0-9]+) ?(?=" + MAG + r")"), r"\1 * "),
    (re.compile(r"(?<![-−\w])([0-9]+) (?=\(e_|\(-|\(−)"), r"\1 * "),
    # trig value followed by \, a space+symbol, \begin{bmatrix}, another trig value, (
    (re.compile(r"(" + TRIG_TEX + r")\\,"), r"\1 * "),
    (re.compile(r"(" + TRIG_TEX + r") \\begin\{bmatrix\}"), r"\1 * \\begin{bmatrix}"),
    (re.compile(r"(" + TRIG_TEX + r")(?=\\(?:cos|sin)\()"), r"\1 * "),
    (
        re.compile(
            r"("
            + TRIG_UNI
            + r") (?=(?:Â|B̂|â|I|i|e₁₂|e_12|v|e_[0-9]|e[₀-₉])(?![A-Za-z0-9_]))"
        ),
        r"\1 * ",
    ),
    (re.compile(r"\br\((?=cos|sin)"), "r * ("),
    (re.compile(r"(" + TRIG_UNI + r") ?· ?"), r"\1 * "),
    # coordinate / coefficient / x,y / r / I before a trig value, a basis vector, a parenthesis
    (re.compile(r"\b([a-z]'?_[0-9])(?=\\(?:cos|sin)\()"), r"\1 * "),
    (re.compile(r"\b([xy]) (?=(?:cos|sin)\()"), r"\1 * "),
    (re.compile(r"\br \((?=cos|sin|\\cos|\\sin)"), "r * ("),
    (re.compile(r"\bI (?=sin\(|cos\()"), "I * "),
    (re.compile(r"\b([a-z]'?_[0-9])(?:\\,| )(?=e_[0-9])"), r"\1 * "),
    (re.compile(r"\b([a-z]_[0-9])(?=[a-z]_[0-9]\b)"), r"\1 * "),
    (re.compile(r"\b([a-z][₀-₉])(?=[a-z][₀-₉])"), r"\1 * "),
    (re.compile(r"\b([a-z]'?_[0-9])\\,(?=\()"), r"\1 * "),
    (re.compile(r"\b([0-9]+[a-z]{0,3})(?: |\\,)(?=e_[0-9]\b)"), r"\1 * "),
    # \vec{a}\,e_{12} , \vec{a}\,(  ;  r\,\big(  ;  )\,e_1 , )\,( , ) e_1 , ) (e_
    (re.compile(r"(\\vec\{[a-z]\}'?)\\,(?=e_|\()"), r"\1 * "),
    (re.compile(r"\br\\,(?=\\big\(|\\Big\(|\()"), "r * "),
    (re.compile(r"\)\\,(?=e_|\(|\\vec)"), ") * "),
    (re.compile(r"\) (?=e_[0-9]|e[₀-₉]|\(e_)"), ") * "),
    # basis-vector chains: e_1 (… , e₁e₂ , e_1 e_2 … e_r , e_r … e_2
    (re.compile(r"\b(e_[0-9]) \((?=e_|-|−|[0-9])"), r"\1 * ("),
    (re.compile(r"(e[₀-₉])(?=e[₀-₉])"), r"\1 * "),
    (re.compile(r"\b(e_[0-9a-z]+) (…|\\cdots|\.\.\.) (?=e_)"), r"\1 * \2 * "),
    (re.compile(r"\b(e_[0-9]+) e_(?=[0-9])"), r"\1 * e_"),
    (re.compile(r"(e[₀-₉]|e_[0-9])…(?=e)"), r"\1 * … * "),
    # middle dot as SCALAR times (left operand a scalar)  ->  *
    # (a lone `c`/`s` is NOT in the list: `c·B` in a Hestenes projection is the inner product
    # of a VECTOR `c` — the maintainer caught that conversion in review, 2026-10-09)
    (
        re.compile(
            r"((?:cos|sin)[²]?\([^()]*\)|\b(?:c1|c2|c3|c12|c13|c23|c123)²?|\b[0-9½]+[a-z]{0,3}"
            r"|θ|⁻¹|²|\bsine|\bcosine|\((?:[0-9]|sin\(|cos\(|\|)[^()]*\)|\|[^|\s]{1,14}\|²?) ?· ?"
        ),
        r"\1 * ",
    ),
    # the sandwich and the unit relation: R v R̃ , R v R⁻¹ , R̃ v R , R R̃ , R̃ R  ->  R * v * R̃ …
    (re.compile(r"\b(R̃|R) ([a-zA-Z]) (R̃|R⁻¹|R\^\{-1\}|R\^-1|R)\b"), r"\1 * \2 * \3"),
    (re.compile(r"\bR (?=R̃\b|R⁻¹)"), "R * "),
    (re.compile(r"\bR̃ (?=R\b)"), "R̃ * "),
    (re.compile(r"\(R/\|R\|\) v \(R/\|R\|\)~"), "(R/|R|) * v * (R/|R|)~"),
    (re.compile(r"\(([a-z]) (e₁₂|e_12|e_\{12\})\)"), r"(\1 * \2)"),
]

POST: list[Rule] = [(re.compile(r"\* {2,}"), "* ")]

ALL_RULES: list[Rule] = RULE1 + RULE3 + RULE2 + POST


def rewrite(text: str) -> str:
    for pattern, repl in ALL_RULES:
        text = pattern.sub(repl, text)
    return text


# --- region filters ------------------------------------------------------------------------

DOCTEST = re.compile(r"^\s*(>>>|\.\.\.)( |$)")
QUOTED = re.compile(
    r"<!-- notation-rule: begin -->.*?<!-- notation-rule: end -->", re.DOTALL
)


def rewrite_text(src: str) -> str:
    """Rewrite everything except the marked spans that quote the rejected spellings."""
    out: list[str] = []
    pos: int = 0
    m: re.Match[str]
    for m in QUOTED.finditer(src):
        out.append(rewrite(src[pos : m.start()]))
        out.append(m.group(0))
        pos = m.end()
    out.append(rewrite(src[pos:]))
    return "".join(out)


def rewrite_python(src: str) -> str:
    """Rewrite only COMMENT and STRING tokens; inside a string, skip doctest lines."""
    out: list[str] = []
    pos: int = 0
    lines: list[str] = src.splitlines(keepends=True)
    offsets: list[int] = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    tok: tokenize.TokenInfo
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        start: int = offsets[tok.start[0] - 1] + tok.start[1]
        end: int = offsets[tok.end[0] - 1] + tok.end[1]
        out.append(src[pos:start])
        piece: str = src[start:end]
        if tok.type == tokenize.STRING:
            piece = "".join(
                part if DOCTEST.match(part) else rewrite(part)
                for part in piece.splitlines(keepends=True)
            )
        else:
            piece = rewrite(piece)
        out.append(piece)
        pos = end
    out.append(src[pos:])
    return "".join(out)


LEAN_COMMENT = re.compile(r"/-[-!].*?-/|--[^\n]*", re.DOTALL)


# In a Lean comment the multiplication star is written WITHOUT surrounding spaces, so it
# visually binds tighter than `+`/`−` (`a₁*b₂ − a₂*b₁`, not `a₁ * b₂ − a₂ * b₁`). A star
# with only whitespace before it on its line is a markdown bullet and is left alone.
TIGHTEN = re.compile(r"(?<=\S) \* (?=\S)")


def rewrite_lean(src: str) -> str:
    """Rewrite only comment spans: block doc comments and line comments."""
    return LEAN_COMMENT.sub(lambda m: TIGHTEN.sub("*", rewrite(m.group(0))), src)


HAND_EDITED: set[str] = {"book/docs/blade-square-sign.rst"}


def main() -> int:
    targets: list[pathlib.Path] = [
        *sorted((REPO / "book/docs").glob("*.rst")),
        *sorted((REPO / "book/docs/notebooks").glob("*.py")),
        *sorted((REPO / "book/figures/epix").glob("*.py")),
        *sorted((REPO / "notebooks").glob("*.py")),
        *sorted(
            p
            for p in (REPO / "src/gacalc").glob("*.py")
            if not re.match(r"g\d+\.py$", p.name)
        ),
        *sorted((REPO / "tools").glob("*.py")),
        *sorted((REPO / "tests").glob("*.py")),
        *sorted((REPO / "proofs/GacalcProofs").glob("*.lean")),
        *sorted((REPO / "tasks/reference").glob("*.md")),
        REPO / "README.md",
        REPO / "CLAUDE.md",
    ]
    changed: int = 0
    path: pathlib.Path
    for path in targets:
        rel: str = str(path.relative_to(REPO))
        if rel in HAND_EDITED:
            continue
        before: str = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            after: str = rewrite_python(before)
        elif path.suffix == ".lean":
            after = rewrite_lean(before)
        else:
            after = rewrite_text(before)
        if after != before:
            path.write_text(after, encoding="utf-8")
            changed += 1
            print(f"rewrote {rel}")
    print(f"{changed} file(s) changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
