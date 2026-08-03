# OpenStax math pedagogy — a survey for "Plotting On Crappy Graph Paper"

**Created:** 2026-08-03 (work record: [[openstax-math-pedagogy-survey]])
**What this is:** how four OpenStax math books actually teach — explanation, worked
examples, exercises, repetition, and how they signal "this result is settled, use it as a
tool" — read from their LaTeX source, plus recommendations for applying it to the GA book.
**Companion:** [[book-outline]] (the book's own plan and five principles) is the intended
reader of this doc's Part II.

## How this was produced (and how to re-run it)

Source: Bill's `latex` branch of four OpenStax repos under `/foo/opt/openstax` (GitHub
mirrors of the openstax org). Each repo carries a Python CNXML→LaTeX converter at
`tools/cnxml2tex/convert.py` that is pure-Python (needs only `lxml`) and runs in-sandbox —
no TeXLive container needed. Regenerate any book's LaTeX with:

```sh
cd /foo/opt/openstax/<repo> && python3 tools/cnxml2tex/convert.py all
```

Books surveyed (collection → repo):

| Book | Collection | Repo | Modules |
|---|---|---|---|
| Prealgebra 2e | `prealgebra-2e` | `osbooks-prealgebra-bundle` | 75 |
| Algebra 1 (HS) | `algebra-1` | `osbooks-algebra-1` | ~130 lessons, 976 files |
| Precalculus 2e | `precalculus-2e` | `osbooks-college-algebra-bundle` | 87 |
| Calculus Volume 1 | `calculus-volume-1` | `osbooks-calculus-bundle` | 55 |

The `sections/` dirs in the multi-book bundles are shared across collections; use the master
`<collection>.tex`'s `\input`/`\subfile` order to know which sections belong to which book.

---

## 0. The headline finding: the LaTeX environment set *is* the pedagogy

Every OpenStax book is generated from CNXML through the same `osbook-envs.sty`, which emits
one LaTeX environment per pedagogical "slot." The environment names are the teaching
structure, and the visual treatment of each encodes its role. This is the single most
transferable idea in the whole survey: **decide your pedagogical vocabulary, give each item
a named environment with a fixed look, and the book writes itself into a predictable shape.**

The shared vocabulary (with the visual grammar from `osbook-envs.sty`):

| Environment | Visual treatment | Role |
|---|---|---|
| `objectives` | titled box, section opener | "Learning Objectives" for the section |
| `definition` | **boxed, thick left rule** | a formal definition |
| `theorem` | **boxed + shaded**, named in brackets | a settled, reusable result |
| `mathrule` | left-rule box, "Rule: …" heading | a named formula/procedure, stated for use, not proved |
| `strategy` | left-rule box, "Problem-Solving Strategy" | a numbered procedural recipe |
| `oscallout{Title}` | gray box, teal run-in title | the general-purpose box (definitions, "How To", rules) |
| `example` + `solution` | titled, usually unboxed | a worked example |
| `checkpoint` / `tryit` | titled | "Try It" — practice immediately after an example |
| `keyconcepts` | titled box | end-of-section prose recap, mirrors `objectives` |
| `keyequations` | titled box, formula table | end-of-section formula table |
| `exercise` + `answer` | plain, auto-numbered | end-of-section practice; answer on odds |
| `calcfig` | centered non-float + `\captionof` | a figure with a teaching caption |
| `calcnote` | run-in note | notes, "How To", "Q&A", "Be Prepared!", media links |

Not every book uses every environment, and *that choice is itself pedagogically telling*:

- **Prealgebra** routes almost everything through `oscallout` + titled `calcnote` and uses
  the `theorem`/`proof` machinery **zero** times. It asserts, boxes, names, and reuses — it
  never proves.
- **Algebra 1** also never uses the specialized `definition`/`theorem` boxes; it funnels
  every settled result into one `oscallout` and lets the *title casing* carry the taxonomy
  (ALL-CAPS = named law, Title-Case = definition/procedure).
- **Precalculus** adds `keyequations` and the "See Example N" back-link spine.
- **Calculus** is the only one that uses the full apparatus: 72 `theorem`s, 58
  `definition`s, 30 written proofs, 17 `strategy` boxes. It is the model for a proof-bearing
  book, which a geometry text is.

**For the GA book:** geometry is theorem-driven, so reinstate the *distinct* `definition`
and `theorem` boxes (already defined in the converter, unused by the algebra texts) rather
than collapsing everything into one callout. See Part II.

---

## 1. Two spines: classic vs. activity-first

Before the dimension-by-dimension detail, one structural fork the four books split on.

**Classic spine** (Prealgebra, Precalculus, Calculus): *teach → worked example → immediate
practice → end-of-section exercises.* Objectives open the section; a real-world hook
motivates; the formal statement is boxed; a "How To" recipe precedes an example that runs
it; a "Try It" follows; exercises close.

**Activity-first spine** (Algebra 1, an Illustrative-Mathematics/Kendall-Hunt curriculum
re-skinned in OpenStax style): the spine is **inverted**. Students *do* a scenario first
(Warm Up → Activity), discover the idea, and only then meet the formal statement — which
lives in a box inside an "Additional Resources" lane alongside conventional worked examples.
Its fixed 7-part lesson skeleton: Overview → Warm Up → Activity (+ "Are you ready for
more?") → Self Check → Cool Down → Practice → Lesson Summary + "Checking In" (reflection).

Both spines are worth stealing from, and they are not mutually exclusive — Algebra 1 runs
*both* in every lesson (discover in the Activity, drill in Additional Resources). The GA
book's own [[book-outline]] principle ("grab attention first; order for engagement, not
logical tidiness") is closer to the activity-first spine, so Algebra 1 is the most relevant
structural model even though Precalculus is the closest reading level.

---

## 2. Dimension 1 — How they explain a new idea

**The dominant pattern, in all four books: real-world hook → concrete instance(s) → boxed
formal statement → figure that confirms it.** The definition box is a *recap for later
reference*, not the first encounter. Definition-first appears only when a topic is built
directly on an already-taught one (e.g. right-triangle trig re-derived from the unit
circle).

Shared traits: first-person-plural "we" and direct-address "you/let's"; short paragraphs;
bold on first use of each term; frequent rhetorical questions; and figures that carry
*teaching captions* ("notice that…"), not bare labels.

**Prealgebra — real-world hook, term boldfaced in prose, then boxed** (`m81326.tex`, angles):

> Are you familiar with the phrase 'do a 180'? It means to turn so that you face the
> opposite direction. It comes from the fact that the measure of an angle that makes a
> straight line is 180 degrees. […] An **angle** is formed by two rays that share a common
> endpoint. […]
> ```
> \begin{oscallout}{Supplementary and Complementary Angles}
> If the sum of the measures of two angles is 180°, then the angles are supplementary. […]
> \end{oscallout}
> ```

**Calculus — stacked concrete cases, then the box** (`m53477.tex`, functions):

> the area of a square is determined by its side length […] The velocity of a ball thrown
> in the air can be described as a function of the amount of time […] The cost of mailing a
> package is a function of the weight […] Since functions have so many uses, it is important
> to have precise definitions […]
> ```
> \begin{definition}
> A function f consists of a set of inputs, a set of outputs, and a rule for assigning each
> input to exactly one output. […]
> \end{definition}

**Calculus even narrates the deferral of rigor** (`m53491.tex`) — a move directly relevant
to the GA book's levels concern:

> We therefore begin our quest to understand limits, as our mathematical ancestors did, by
> using an intuitive approach. At the end of this chapter, armed with a conceptual
> understanding of limits, we examine the formal definition of a limit.

**Algebra 1 — the hook is emotional and concrete, and the lesson opens by *doing*** (`m01874`):

> Anna's class entered a contest where they had to build a catapult and use it to launch a
> pumpkin at a distant target. But when Anna's class shot their pumpkin for the first time,
> it went wildly off course. […] If Anna's class used a quadratic equation, they could
> mathematically find the best place and angle […] Their accuracy went from 2% to 99%.

**Named-person hooks** recur (Precalculus opens conics with Katherine Johnson computing
orbital parabolas). The takeaway: motivation is a person or a stake, not "this topic is
important."

---

## 3. Dimension 2 — The anatomy of a worked example

**The canonical worked example is: bold descriptive title → problem statement (often
multi-part `(a)/(b)`) → solution with each step spelled out → an immediately-following "Try
It" on a parallel problem, answer supplied.** Two solution formats recur, and both matter
for geometry:

**Format A — the two-column "board talk": left column says what a teacher would say aloud;
right column is the actual math.** Prealgebra's preface states the intent outright: "Most
examples are written in a two-column format, with explanation on the left and math on the
right to mimic the way that instructors 'talk through' examples as they write on the board."

Prealgebra (`m81244.tex`, column addition), left column verbatim:

> | (action) | (math) |
> |---|---|
> | Write the numbers so the digits line up vertically. | 43 / +69 |
> | Add the ones: 3+9=12. Write the 2, carry the 1 ten. | … |
> | Now add the tens: 1+4+6=11. | 112 |

Precalculus (`m49366.tex`), the same format with a *reason* per line:

> ```
> 5^{x+2}=4^{x}          There is no easy way to get the powers to have the same base.
> ln 5^{x+2}=ln 4^{x}    Take ln of both sides.
> (x+2)ln5 = x ln4       Use laws of logs.
> x ln5 + 2ln5 = x ln4   Use the distributive law.
> x ln5 - x ln4 = -2ln5  Get terms containing x on one side, terms without x on the other.
> x(ln5 - ln4) = -2ln5   Factor out an x.
> x = ln(1/25)/ln(5/4)   Divide by the coefficient of x.
> ```

**This "statement | reason" two-column format is the same genre as a two-column geometry
proof.** It is the single most geometry-relevant formatting device in the whole survey — a
GA derivation and a geometry proof both read naturally as action-left / justification-right.

**Format B — badge + numbered "Step N" prose**, used for multi-step procedures (Algebra 1,
`m00966`). A hard task is decomposed across *several small examples* (identify → substitute →
rearrange), one micro-skill each, rather than one big example. Every step carries its
reason ("Write the x term before the y term").

**The Try-It is welded to the example.** In Prealgebra the ratio is exact: **1473 "Try It"
to 737 examples = exactly two Try-Its per worked example.** Precalculus has ~490. The Try-It
restates the example's title and gives the same task type, with the answer (and often the
full worked solution in the identical step format) in the box. The student sees the exact
template they are expected to reproduce.

**Verification is modeled as part of the solution.** Examples routinely end with an explicit
**Check** step ("Substitute 5 for x… 14=14 True ✓"). For a geometry/GA book, end a
construction or derivation with an explicit "why this is valid" line.

**Calculus adds a cross-representation example**: compute a limit from a *table* of values,
narrate reading the columns, then *confirm with a graph* (`m53491.tex`). Showing the same
fact in two representations and checking them against each other is a strong habit to copy.

---

## 4. Dimension 3 — How exercises are structured and ordered

**The exercises are ordered by cognitive type, easy→hard, and mapped back to the examples.**

**Precalculus states the canonical order explicitly** (preface): *Verbal → Algebraic →
Graphical → Numeric → Technology → Extensions → Real-World Applications*, each category
defined ("Verbal = assess conceptual understanding of key terms"; "Extensions = more
challenging… synthesize multiple objectives"). Each group opens with a shared lead-in ("For
the following exercises, …") and is laid out two-up (`multicols`). This maps cleanly onto
geometry: **Vocabulary → Diagram-reading → Construction/Drawing → Proof → Extensions →
Applications.**

**Prealgebra's per-section quartet** is a fixed template: *Practice Makes Perfect* (grouped
by learning objective, with headers copied verbatim from the section's own objective titles,
even/odd paired, answers on odds) → *Everyday Math* (applications) → *Writing Exercises*
(verbalize the concept; answers "Answers will vary") → *Self Check* (a metacognitive mastery
checklist: "What steps will you take to improve?").

**Exercise↔example pairing is mechanical and explicit.** Practice-set sub-headers are copies
of the in-section subsection titles, and the exercise instruction sentence is copied from
the example ("Use the Pythagorean Theorem to find the length of the hypotenuse" appears as
both an example and an exercise instruction). Students are meant to recognize the connection
at a glance.

**Chapter-level review** (classic-spine books): a *Chapter Review Exercises* set
**subdivided by source section** (each block re-headed by a `\cref` to the section, so a
student can trace a weakness back to where it was taught), followed by a *Practice Test*
that is deliberately **not** organized by section and is "weighted toward cumulative
objectives" — i.e. it simulates an exam. Precalculus and Prealgebra both do this; Calculus
keeps review per-section instead.

**Algebra 1** grades its four venues by cognitive demand instead: Warm Up (discuss) →
Activity (construct, with an "Are you ready for more?" enrichment tier) → Self Check (one MC
item) → Practice (formal, two-column, MC-heavy) → per-unit Project.

**Conventions worth adopting wholesale:** odd-numbered answers in the back; a `[T]`-style
inline tag for technology/calculator problems (Calculus has ~400); and reserving the *last*
items in each set for conceptual "explain why / draw a counterexample" work.

---

## 5. Dimension 4 — How much repetition, and at what scale

Reinforcement is layered at **four time-scales**, and every rule appears **at least twice**:

1. **Immediate:** every technique's example is chased by a Try-It on a near-identical
   problem, and (Precalculus) often a **Q&A box** pre-empting the predictable misconception
   ("Do all linear functions have y-intercepts? *Yes. […]*").
2. **Point-of-use:** a rule is restated *where it is used*, and the book says so out loud —
   Prealgebra: "We introduced the Subtraction and Addition Properties of Equality in §Y. […]
   Let's review those properties here," then re-boxes them and `\cref`s the origin rather
   than re-deriving. Mnemonics are given at the moment of need (SohCahToa inline).
3. **End-of-section:** `keyconcepts` (prose recap) + `keyequations` (formula table) + Key
   Terms glossary. The `keyconcepts` bullets **mirror the opening `objectives` one-for-one**
   — the section is bookended by the same statements, first as goals, then as a checklist.
4. **End-of-chapter / prerequisite:** cumulative review + practice test; and the
   **readiness gate** at the front. Prealgebra opens every section (from §1.2 on) with a
   **"Be Prepared!"** quiz whose items are the exact sub-skills the section will compose,
   each hyperlinked back to the specific earlier example that teaches it. It is spaced
   retrieval *and* a preview of the day's ingredients. Algebra 1 does the same with
   per-unit readiness mini-lessons.

The books also **re-anchor explicitly before reusing** a result: "Recall" appears 80 times
in Precalculus, "we know that" 25, "we learned" 11. Nothing is assumed to still be in the
reader's head.

Algebra 1 adds **metacognitive spacing**: every lesson ends with "Checking In" ("On a scale
of 1 to 5, how confident do you feel…?") and growth-mindset asides ("Nobody is good at this
on the first try"). Cheap to add, and it fits the GA book's stated warmth.

---

## 6. Dimension 5 — Signaling a "settled result" (the black-box grammar)

This is the heart of the survey and the direct answer to the levels-of-abstraction concern:
*how does a textbook let a student trust a proven result and move up a level, instead of
staying trapped in its mechanics?* Calculus Volume 1 is the model, because it is the only
one of the four that carries real proofs. Six cooperating mechanisms:

### 6.1 The keeper is boxed; the justification is not

`theorem` is a **shaded, ruled box**; the proof is rendered as an ordinary
`\subsubsection{Proof}` in plain body text *after* the box, ended by a hand-written `$\square$`.
The visual grammar alone says: **box = keep this; unboxed "Proof" text = optional.** A
student can read the box, skip to the next example, and lose nothing operational.

Each theorem also carries a **human-readable name** in brackets and a `\label`, and states
the result in **multiple registers at once** — Calculus's Product Rule box gives Leibniz
notation, prime notation, *and* a plain-English paraphrase before any proof (`m53575.tex`):

> ```
> \begin{theorem}[{{Product Rule}}]
> Let f(x) and g(x) be differentiable functions. Then
>   d/dx(f(x)g(x)) = d/dx(f(x))·g(x) + d/dx(g(x))·f(x).
> That is, if j(x)=f(x)g(x), then j'(x)=f'(x)g(x)+g'(x)f(x).
> This means that the derivative of a product of two functions is the derivative of the
> first function times the second function plus the derivative of the second times the first.
> \end{theorem}
> ```

### 6.2 The decision of *what to prove* is narrated in one sentence

Only ~42% of Calculus's theorems (30 of 72) get a written proof. The rest are stated as
black boxes, and the book *says so*, in a single repeatable sentence that gives the student
permission to trust:

- "The proof of the quotient rule is very similar to the proof of the product rule, so it is
  omitted here. Instead, we apply this new rule […] in the next example." (`m53575.tex`)
- "We provide only the proof of the sum rule here. The rest follow in a similar manner."
- "The proof of the extreme value theorem is beyond the scope of this text." (`m53611.tex`)
- "…which we state without proof." (`m53596.tex`)

### 6.3 Later work invokes a settled result *by name*, without re-deriving

Once boxed, a theorem is used as a citation ("By the Intermediate Value Theorem…", "by the
extreme value theorem (see §…)"). Calculus Vol 1 has 485 such `\cref`s. This is exactly the
SSS/SAS/"vertical angles are congruent" chaining a geometry course runs on.

### 6.4 New proofs are *assembled from* earlier black boxes

The clearest demonstration is the Mean Value Theorem cluster (`m53612.tex`): MVT's proof is
"reduce to Rolle's theorem"; its Corollary 2's proof invokes Corollary 1 as a settled fact;
and the Fundamental Theorem of Calculus is proved using the MVT-for-Integrals proved earlier
in the *same* section, then immediately *applied* as a black box in the next example. A proof
is shown to be a short argument built from named, already-trusted pieces — the opposite of
grinding mechanics.

### 6.5 Procedures get their own settled-object box: "Problem-Solving Strategy"

A `strategy` box states a numbered procedure, and **the very next example follows those exact
numbered steps** (Calculus's optimization strategy → "Maximizing the Volume of a Box," whose
solution is literally "Step 1: … Step 2: …"). This is the computational analogue of a
theorem: a reusable recipe you invoke without re-justifying. Precalculus's "How To" boxes are
the same device (How-To → Example that runs it step-for-step → Try-It), and this **How-To →
Example → Try-It triad is the backbone of the classic-spine books.** For geometry: "How to
bisect an angle" → worked bisection → "Try it on this angle."

### 6.6 Teaching *when* a result may be applied — checking the hypotheses

Right after the IVT, Calculus runs examples titled **"When Can You Apply the Intermediate
Value Theorem?"** that deliberately show cases where the hypotheses fail (`f(x)=1/x` on
`[-1,1]` — not continuous, so the theorem does not apply). The black box comes with a lesson
in reading its label before pressing the button. Geometry needs this constantly ("is this
figure actually a parallelogram before you use its properties?").

### The four tiers of engagement (the structural answer to "multiple levels")

Calculus lets a reader stop at any of four tiers for any result, and names the first two as
*separate learning objectives* ("State the meaning of the FTC" vs. "Use the FTC to evaluate
derivatives"):

1. **Trust** — the boxed, named theorem/rule (multiple notations + plain English). Read this
   and you can compute.
2. **Understand-why** — the unboxed, skippable proof.
3. **Do-the-mechanics** — worked examples with reason-annotated steps + a terse checkpoint;
   `strategy` boxes turn procedures into numbered recipes.
4. **Consolidate** — end-of-section Key Concepts (prose) + Key Equations (table).

The proof is packaged so it never traps a student in mechanics: physically outside the box,
often absent by explicit choice, never required by the examples that follow it. **This is the
exact affordance the GA book needs.**

---

## 7. Dimension 6 — Print-and-draw affordances (and the gap to beat)

All four books are *drawing-heavy in intent* but *read-only in the artifact*, and this is
the clearest place for the GA book to do better than OpenStax.

**What they do well:**
- **Drawing is baked into the method.** Prealgebra's geometry problem-solving strategy makes
  "Draw the figure and label it" literal **Step 1** of every solution. Calculus's optimization
  strategy step 1: "If applicable, draw a figure and label all variables." Precalculus's
  trig How-To step 1: "If needed, draw the right triangle and label the angle provided."
- **Imperative draw/sketch/label prompts everywhere** (Precalculus: sketch 209, draw 182,
  Plot 81, label 40; Algebra 1: 100+ "sketch/draw/plot"; Calculus similar).
- **"Label the parts" exercises** whose whole body is a figure and whose answer is the same
  figure annotated (Precalculus's "label the adjacent side, opposite side, and hypotenuse").
- **Read-from-graph exercises** ("use the graph to find the values… estimate when necessary").
- **Fill-in tables to complete then plot** — Calculus ships a partial value table with the
  literal cell "Use additional values as necessary," then "sketch the graph with the aid of
  the tables given."
- **Construct-from-constraints prompts** whose answer is "Answers may vary" — pure hand-drawing
  ("draw a graph, continuous on [-4,4], with an absolute max at x=2 and minima at x=±3").
- **Physical construction** (Precalculus's thumbtack-and-string ellipse).

**The gap:** figures are pre-rendered raster JPGs centered at `.6\textwidth`. The book shows
a *finished* picture; it almost never supplies a **blank grid, blank number line, or
un-annotated construction figure** for the student to draw *on*. Algebra 1's report flagged
this as its single biggest shortfall (`\square` fill-in box appears in exactly 1 file).

**For a book literally titled "Plotting On Crappy Graph Paper," this gap is the opportunity.**
Ship blank coordinate grids, blank/relative graph paper, blank number lines, dot/iso paper,
and un-annotated labeled-diagram templates as first-class printable elements — the thing every
OpenStax book gestures at but none provides.

---

## 8. Dimension 7 — Moving between mechanics and concept

Beyond the black-box grammar of §6, the books share concrete habits for letting a reader move
between altitudes on purpose:

- **Concrete → symbolic as the exercise itself.** Algebra 1's pizza activity walks a student
  from "what's your favorite pizza?" → a numeric cost expression → "replace the quantities
  that might change with letters" → a symbolic formula → "what do the letters represent?" The
  abstraction step *is* the task, not a leap the reader must make alone.
- **Mechanics quarantined from concept.** Algebra 1 puts conceptual discovery in the Activity
  and procedural drill in a separate "Additional Resources" lane; a reader engages at either
  altitude.
- **Black-box-then-justify.** Algebra 1 *uses* the quadratic formula for whole lessons, then a
  later lesson derives it, framed as understanding rather than a gate to use — "we told you it
  works; here's why." Calculus derives the ellipse/parabola equation once, freezes it into a
  boxed standard form, and thereafter only cites it.
- **Same object at two levels.** Precalculus builds right-triangle trig by *reinterpreting* the
  unit-circle definitions as side ratios — the same sine, seen two ways.
- **Multiple representations as first-class** (verbal / table / graph / symbolic), taught with
  an explicit "each is useful for different reasons" table.

---

## Part II — Applying this to the GA book

### 9. Where the GA book stands today (from the code survey)

- The book *"Plotting On Crappy Graph Paper"* (`book/docs/`, Sphinx) is **~85% placeholder**.
  Only three prose chapters are written: `rotate.rst`, `geometric-product.rst`,
  `proof-rotate.rst`. The mature teaching prose currently lives in the *standalone*
  `notebooks/display*.py`, aimed at a library-demo audience, not the print student.
- **Two registers already coexist**, exactly like OpenStax's: the library docstrings in
  `src/gacalc/base.py` are **mechanics-first** (Hestenes-cited component formulas — "the
  lowest-grade part of the geometric product ⟨AB⟩_|r−s|"), while the notebooks and written
  chapters are **concept-first** (FOIL analogy for the geometric product; "to rotate is
  simply to multiply by R — an action, not just a number").
- **The rotation ladder is the one place the black-box climb is already built:**
  `proof-rotate.rst` derives rotation from high-school trig *in coordinates*, then
  `geometric-product.rst` *reuses* that result to define the geometric product, then rotation
  is *redefined* on top of the geometric product. This is precisely the OpenStax "derive once
  in coordinates, box it, throw the coordinates away, climb up" move — you already do it once.
- **There are no exercises or worksheets anywhere.** This is greenfield.
- `associativity` is already flagged in `displaymv.py` as a result that "we should prove …
  not just take on faith" (deferred to [[prove-associativity-of-multiplication]]) — the right
  instinct, matching Calculus's "state what to prove out loud."

### 10. Recommendations, in priority order

**(1) Build the environment vocabulary first, then write into it.** Before writing chapters,
define the GA book's pedagogical slots as named, fixed-look elements (Sphinx directives /
LaTeX environments): `definition`, `theorem` (boxed, named, cross-referenceable), a
`howto`/`strategy` recipe box, `example` + `tryit`, `keyconcepts`, `keyequations`,
`bepreparedreadiness`. Geometry is theorem-driven, so **use distinct `definition` and
`theorem` boxes** — do not collapse them into one callout the way Algebra 1 does. This makes
every later chapter fall into a predictable shape and is the highest-leverage step.

**(2) Adopt the box/unbox grammar to solve the levels-of-abstraction problem directly.** This
is the answer to your dot-product worry. For every GA operator:
   - State the result in a **boxed theorem**, named, with the geometric meaning in plain words
     *and* the formula (multiple registers, as Calculus does).
   - Put the derivation in **unboxed, skippable "Proof" text** after the box, ending in `∎`.
   - Where a derivation is routine or heavy, **say so in one sentence** and defer it ("the
     same argument as §X gives…", "we verify this in the calculator; the hand proof is in
     Appendix Y") — giving the reader explicit permission to trust and move up.
   - Thereafter **invoke the result by name**, never re-deriving ("by the
     projection-product identity…").
   This is the structural cure for students fixating on mechanics: the mechanics are visibly
   *optional* and *below* the boxed result they feed.

**(3) Make [[dot-wedge-projection-rejection]] the worked archetype of the
climb.** (Proved and verified 2026-08-03; the work record is archived at
`tasks/archive/2026/08/03/verify-dot-wedge-as-projection-rejection-products.md`.) That
result — split `a` relative to `b`, and the geometric product of the projection
is the dot product while the geometric product of the rejection is the wedge — is the perfect
first demonstration of the box/unbox grammar:
   - **Box:** "Dot and wedge are the parallel and perpendicular parts of the geometric
     product," stated with the picture.
   - **Unboxed proof:** the two-line argument (parallel ⇒ zero wedge; perpendicular ⇒ zero
     dot), verified symbolically in gacalc.
   - **Reuse:** from then on, treat `ab = a·b + a∧b` as the settled decomposition and build
     projection/reflection/rotors on top without reopening it.
   Write it once, box it, and every later chapter cites it. This single example teaches the
   *method* of black-boxing as much as the fact.

**(4) Use the How-To → Example → Try-It triad as the chapter backbone, with two-column
solutions.** For each GA technique: a numbered recipe box ("How to reflect a vector across a
plane"), an example that runs the steps by number, then a "Try It" with the answer. Write the
worked steps as **two-column "action | reason"** — this format doubles as a geometry-proof
format and keeps the *why* attached to every mechanical step, which is exactly what stops a
student from drowning in the manipulation.

**(5) Fill the print-and-draw gap that every OpenStax book leaves.** The book's title is a
promise: ship **blank and relative graph paper, blank number lines, un-annotated vectors, and
blank bivector/oriented-area templates** as printable pages. Your `nbplotutils.py` already
draws graph paper, relative graph paper, labeled triangles, and per-blade number lines — add a
"blank / draw-it-yourself" mode that emits the grid and axes *without* the answer, as the
worksheet counterpart to each figure. Bake "draw and label the vectors" into the solution
method as literal Step 1, the way OpenStax bakes in "draw the figure."

**(6) Lead every chapter with a hook, define second — and lean into engagement-first
ordering.** This matches [[book-outline]] principle 1 and the Algebra 1 spine: open with the
picture/stake (a rotation, a reflection, a real measurement), let the reader *do* something,
and box the definition afterward. Reserve definition-first for topics built directly on an
earlier one (as Precalculus does for right-triangle trig).

**(7) Repeat at the four scales and bookend each chapter.** Open with objectives and a "Be
Prepared!" readiness check whose items are the exact prerequisites the chapter composes
(cross-linked to where each was taught); close with a Key Concepts recap that mirrors the
objectives one-for-one, plus a Key Equations table of the chapter's boxed results. Restate a
rule at its point of reuse and say "recall §X" rather than re-deriving.

**(8) Order exercises by cognitive type, geometry-flavored.** Vocabulary → Diagram/figure
reading → Construction & drawing (print-and-draw) → Proof (two-column) → Extensions →
Applications. Answers on odds; reserve the last items for "explain why / draw a
counterexample." None of this exists yet, so it can be built to this shape from the start.

**(9) Teach *when* an identity applies, not just the identity.** Borrow Calculus's "When can
you apply this?" examples — show a case where a GA identity's precondition fails (e.g. an
operation defined only for blades, applied to a general multivector), so students learn to
read a result's label before using it.

### 11. A concrete sketch: the "dot product" section, rebuilt to this grammar

To make the recommendations concrete, here is how one section could read — the operator you
named as the trap:

1. **Hook / picture:** two vectors on graph paper; "how much of one points along the other?"
   Drag the angle; watch a number. (Print-and-draw: a blank graph-paper worksheet with two
   vectors to measure.)
2. **Concept-first statement, boxed:** *Definition — the dot product `a·b` is the scalar part
   of the geometric product; geometrically, it is the signed length of the projection of `a`
   onto `b`, times `|b|`.* Stated in words and symbols.
3. **The climb, boxed as a theorem** (this is [[dot-wedge-projection-rejection]]):
   *`a·b` is the geometric product of `a`'s projection onto `b` with `b`; `a∧b` is the
   geometric product of `a`'s rejection with `b`.*
4. **Unboxed, skippable proof:** the two-line parallel/perpendicular argument, plus a gacalc
   cell that verifies it symbolically. A sentence gives permission: "If you just want to use
   the dot product, skip to the examples — this box is settled."
5. **How-To + Example + Try-It:** "How to compute a dot product from components," an example
   run step-by-step in two-column form, a Try-It with answer.
6. **Black-box from here on:** the rest of the book writes `a·b` and `ab = a·b + a∧b` as
   settled, never reopening the component grind. Projection, reflection, and rotors are built
   *on top of* the boxed identity.

The point the student should leave with is not the component formula; it is that the dot
product is one proven face of the geometric product, and they may now use it without looking
inside. That is the whole levels-of-abstraction lesson, delivered by the box/unbox grammar
rather than by exhortation.

---

## Appendix — pointers back to source

- Environment definitions and visual grammar: `osbook-envs.sty` (identical across the four
  repos), header comment at lines 5-18.
- Book prefaces (each book's own pedagogy spec): Prealgebra `m81241.tex`, Precalculus
  `m50919.tex`, Calculus `m60027.tex`.
- Richest single specimens: the Calculus theorem/proof grammar (`m53575.tex` Product Rule,
  `m53612.tex` MVT cluster, `m53632.tex` FTC); the Precalculus How-To→Example→Try-It triad
  (`m49440.tex` parabola); the two-column reason-annotated solution (`m49366.tex`,
  `m53492.tex`); Prealgebra's readiness gate and per-section quartet (`m81326.tex`).
- GA book current state: `book/docs/` (Sphinx skeleton), `notebooks/display*.py` (mature
  prose), `src/gacalc/base.py` (mechanics-first docstrings), [[book-outline]] (the plan).
