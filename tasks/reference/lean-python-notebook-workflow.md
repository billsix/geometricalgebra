# The Lean → symbolic Python → student proof-notebook workflow

What gacalc's three forms of every result are for, how a Lean theorem and its Python twins are kept
in step, and what makes a proof notebook something a student can verify. The author's side comes
first, then the student's. The mechanics of building notebooks are in
`tasks/reference/book-and-docs-pipeline.md`; how a notebook's cells teach is in
`tasks/reference/book-notebook-teaching-style.md`. This doc does not repeat either.

## Why there are three forms

The maintainer (William Emerison Six <billsix@gmail.com>) reads Hestenes & Sobczyk, and MacDonald
where Hestenes moves too fast. From that reading he writes Python that works with numbers and with
sympy symbols, then uses it in graphics work such as modelviewprojection. The open question was
always whether the Python, and his reading of the book, are right ("am I doing projection
right?"). Lean answers that. It is not used to prove anything new, and students are not expected to
read it. The audience is the book *Geometry 2*: a pre-linear-algebra course for high-school and
early college students.

So each result comes in three forms (`CLAUDE.md`, "Every piece of math comes in three forms"):

1. **Lean** (`proofs/GacalcProofs/`) checks the *idea*: the identity holds for every input.
2. **Symbolic Python** (a test in `tests/`, a book notebook in `book/docs/notebooks/`) checks the
   *code*: gacalc's operations, run on symbols, give the same identity.
3. **Prose + LaTeX** (`book/docs/*.rst`) tells the student, and names the Lean theorem.

Lean does not check the Python. "Lean checks the idea, the tests check the code"
(`tasks/reference/lean-for-gacalc.md`, "The one thing to understand first"). What ties the two
together is that they state the same identity. The twin tags below make that link something you can
find with grep.

## Author side: twin tags, and managing drift

**The convention** (William Emerison Six <billsix@gmail.com>, 2026-11-18): each Lean theorem that
has Python twins carries a tag, and each twin carries the identical tag. The tag is
`twin: <the theorem's fully qualified Lean name>`, written as a comment in each language:

- Lean: a `--` comment on the line above the theorem (above its `/-- … -/` doc comment, if any):
  `-- twin: GacalcProofs.G3.projectSP_eq_proj`.
- A test: a `#` comment on the line above the test function.
- A book notebook: a `#` comment in its first code cell, so the student does not see it in the
  rendered page. The page's Markdown still names the theorem in prose.

The worked example is the projection trio:

| Form | Where |
| --- | --- |
| Lean | `proofs/GacalcProofs/StandardPosition.lean` (`projectSP_eq_proj`, `rejectSP_eq_reject`) |
| Test | `tests/test_standardposition.py` (the two `*_matches_canonical_symbolic` tests) |
| Notebook | `book/docs/notebooks/proof-projection.py` |

Older pairs cite each other in prose ("the runnable twin of …" in a test module docstring, "Python
`standardposition.project_sp`" in a Lean doc comment). Give such a pair a tag when you next touch
it; nothing requires a backfill.

**Finding the twins.** `git grep -n "twin: GacalcProofs.G3.projectSP_eq_proj" -- '*.py' '*.lean'` lists every member
(the pathspec leaves out this doc's own examples).
To find orphans, list each tag with its count: a tag that appears only once has lost its other
side.

```sh
git grep -h -o "twin: GacalcProofs[A-Za-z0-9_.']*" -- '*.py' '*.lean' | sort | uniq -c | sort -n
```

There is no checker script and no gate. The decision was grep, not a tool.

**What counts as drift, and what to do about it.** Change one member's statement (its hypotheses,
its conclusion, the operation's name or argument order) or rename the theorem, and the twins no
longer state the same thing. When you edit a tagged member, grep its tag and bring the others in
line in the same change: rename the tag everywhere, change the test's assertion, change the
notebook's check. A Lean proof whose *proof* changes but whose statement does not leaves its twins
alone.

## Student side: verify, don't derive

A proof notebook does not ask the student to find the proof. It shows every mechanical step so the
student can **check** each one; producing the steps is the tedious part, and that is the computer's
job. For example, 𝒢₂ associativity is shown by writing out every component-wise product and letting
the student watch the terms cancel. What makes a notebook checkable:

- **Exact, canonical forms.** Symbols and exact rationals, never decimals. Every step uses symbolic
  coordinates, and numbers appear only in figures (`book-notebook-teaching-style.md`, "Symbolic
  notebooks").
- **One move per row.** A `show_mult(a, b)` table (`src/gacalc/nbdisplay.py`) gives one
  distributive or anticommuting move per row, so each row can be checked alone. It is shown first at
  the plot values, short enough to check by hand, then symbolically.
- **Both sides before their difference.** A check prints the left side and the right side, then
  their difference simplifying to `0` (`CLAUDE.md`, "Book: one name per operation"). A bare `0` on
  its own shows nothing.

**Not built yet: showing the cancellation itself.** The maintainer (2026-09-30) noted that an
associativity notebook that prints the two expansions and then `0` "doesn't show" the cancellation.
The goal is to lay the two sides out term by term and mark matching terms with
`\underbrace{…}_{\text{cancel}}`, which MathJax and myst-nb render. The display helper and the first
prototype, on distributivity, are the job of `tasks/investigate-lean-to-python-proof-notebooks.md`.
That task's decision is that the notebook does the symbolic expansion and cites the Lean theorem
that certifies it; it is not transcribed from Lean's steps. A `ring` proof has no steps to
transcribe.

**Where a proof notebook lives.** The book's rule is "proofs → separate `.rst`; uses → main docs;
calculations → notebooks" (`tasks/reference/book-outline.md`). A proof is a `proof-*.rst` page, and
its calculations are the companion `book/docs/notebooks/proof-*.py`, linked from the page. Examples
are `proof-projection`, `proof-cross` and `proof-reciprocal-frame`. There is no separate
proof-notebook directory.

## Cross-links

- `tasks/reference/lean-for-gacalc.md`: Lean orientation, and what a proof does and does not check.
- `tasks/reference/lean-ga-proof-architecture.md`: how the Lean corpus is built.
- `tasks/reference/book-notebook-teaching-style.md`: how a book notebook's cells teach.
- `tasks/proof-notebooks-student-math-notation-style.md`: the proof-notebook umbrella this doc came
  from.
- `tasks/archive/2026/11/18/reference-doc-lean-workflow-and-proof-notebooks.md`: the task that wrote
  this doc.
