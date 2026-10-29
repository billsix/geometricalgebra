# The order math is taught: operations and properties, Algebra 1 → Algebra 2

**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**What this is:** the canonical sequence in which a standard US school algebra
curriculum introduces the *operations* and the *algebraic properties* (commutative,
associative, identity, inverse, distributive), distilled into ordering principles for
sequencing the from-scratch geometric-algebra Lean files `G1.lean`/`G2.lean`/`G3.lean`.
It answers "what order would a student expect to meet these ideas in?" so the proof
files can mirror it.
**Companion:** [[openstax-math-pedagogy]] (how the same OpenStax books *teach* — prose,
worked examples, the box/unbox grammar — for the GA *book*). This doc is about *concept
ordering for the proof files*; that one is about *teaching style for the book*. Read both
when touching either.
**Drove:** the reorder `tasks/archive/2026/10/29/reorder-gn-lean-to-teaching-order.md` (completed
2026-10-29 — reordered the Lean files to this sequence with no change to any statement or proof).

## How this was produced (and how to re-check it)

Two sources, agreeing:

1. **Web survey** (2026-10-28) of standard Algebra 1 / Algebra 2 scope-and-sequence and
   "properties of real numbers" lessons. The core finding is uniform across publishers:
   the five properties are a single early "Foundations" unit, taught per-operation with
   **addition before multiplication**, and **commutative/associative before
   identity/inverse before distributive**.
2. **The in-house pedagogy anchor** — the maintainer's OpenStax ports in **impo**
   (https://github.com/billsix/impo), the same source [[openstax-math-pedagogy]] draws
   on. OpenStax *Elementary Algebra 2e* is authoritative here because the GA project
   already treats these books as its curriculum baseline.

OpenStax *Elementary Algebra 2e*, Chapter 1 "Foundations", section order (verbatim):

| § | Section |
|---|---|
| 1.1 | Introduction to Whole Numbers |
| 1.2 | Use the Language of Algebra |
| 1.3 | **Add and Subtract Integers** |
| 1.4 | **Multiply and Divide Integers** |
| 1.5 | Visualize Fractions |
| 1.6 | Add and Subtract Fractions |
| 1.7 | Decimals |
| 1.8 | The Real Numbers |
| 1.9 | **Properties of Real Numbers** |
| 1.10 | Systems of Measurement |

And §1.9's own objective order (verbatim), each pair presenting **addition before
multiplication**:

1. Use the **Commutative and Associative** Properties (commutative: addition, then
   multiplication; associative: addition, then multiplication)
2. Use the **Identity and Inverse** Properties of Addition and Multiplication (identity:
   addition then multiplication; inverse: addition then multiplication)
3. Use the **Properties of Zero** (multiplication by zero; division of/by zero)
4. Simplify Expressions Using the **Distributive** Property

(The end-of-section summary table re-lists them commutative, associative, distributive,
identity, inverse — a recap order, not the teaching order. The *teaching* order is the
numbered objectives above.)

## Part I — The canonical sequence

### Operations, in teaching order

Addition and subtraction are taught **before** multiplication and division — for integers
(§1.3 before §1.4) and again for fractions (§1.6 "add and subtract" before the multiply
lesson). Multiplication is introduced as *repeated addition*, so addition is its
prerequisite, not a sibling. Division comes with/after multiplication (as its inverse).

> **Order:** addition → subtraction → multiplication → division. Then negation (additive
> inverse) and reciprocal (multiplicative inverse) sit under the Inverse property.

### Properties, in teaching order

1. **Commutative** — `a + b = b + a`; `a·b = b·a` (addition stated first).
2. **Associative** — `(a+b)+c = a+(b+c)`; `(a·b)·c = a·(b·c)` (addition first).
3. **Identity** — additive identity `0` (`a + 0 = a`) before multiplicative identity `1`
   (`a·1 = a`).
4. **Inverse** — additive inverse `−a` (`a + (−a) = 0`) before multiplicative inverse
   `1/a` (`a·(1/a) = 1`, `a ≠ 0`).
5. **Properties of zero** — `a·0 = 0`; `0/a = 0`; `a/0` undefined.
6. **Distributive** — `a(b+c) = ab + ac`. Taught **last** of the group, because it is the
   one property that *links* the two operations, so it presupposes both.

A standing scope note every text makes explicit: **commutative and associative hold only
for addition and multiplication, not subtraction or division.** Subtraction/division are
handled as "add the opposite" / "multiply by the reciprocal" precisely so the properties
transfer.

### Algebra 2 macro arc (for context)

Algebra 2 does not re-teach the properties; it opens with a brief "basic concepts /
equations & inequalities" review that *cites* them, then moves to functions (linear,
quadratic, polynomial, radical, rational), then exponential/logarithmic, then
sequences/series and (often) trig and complex numbers. The relevant lesson for file
ordering is Algebra 1's Foundations unit above; Algebra 2's contribution is the habit of
**stating a settled property once and thereafter invoking it by name** — the same
black-box move [[openstax-math-pedagogy]] §6 describes.

## Part II — The ordering principles (what to apply to the Lean files)

Distilled from Part I, in priority order:

1. **Define a thing before the first thing that uses it.** (Trivially forced by Lean, but
   it is also the pedagogical rule: numbers → operations → properties → results.)
2. **Addition/subtraction before multiplication/division.** A student meets `+` before
   `·`. In GA this means: the vector-space operations (`add`, `sub`, `neg`, `smul`) come
   *before* the geometric product `mul` and the wedge.
3. **State a property right where its operation is introduced, per-operation, addition
   first** — not hoisted into a separate "laws" collection. Commutative/associative of
   addition belong with `add`; the product's associativity/distributivity belong with
   `mul`.
4. **Within the property group: commutative → associative → identity → inverse →
   zero → distributive.** Distributive last, because it is the bridge between `+` and `·`
   and needs both already on the table.
5. **Identity before inverse; the additive form before the multiplicative form.**
6. **Concrete before abstract, specific before general.** Numbers before variables;
   `G1` (1-D, commutative, the degenerate twin) reads as the warm-up for `G2`/`G3`.
7. **Name a settled result, then reuse it by name** — do not re-derive. (Algebra 2 habit;
   matches the project's existing box/unbox intent.)

## Part III — Where the GA Lean files stand against this

**State after the 2026-10-29 reorder** (William Emerison Six <billsix@gmail.com>;
`proofs/GacalcProofs/`): the files now **follow** this teaching order. `G1.lean`/`G2.lean`/
`G3.lean` each read: representation scaffolding → **addition and the vector-space operations**
(`add`/`sub`/`neg`/`smul`) → **the geometric product, the wedge, and the dot** → reverse and
magnitude → **the algebra laws, stated with each algebra** (associativity, two-sided
distributivity, identity, the scalar laws), with `vec_anticomm_perp` placed beside the
wedge/anticommutativity material it rests on.

What changed (a pure relocation — no statement, proof, or name altered; `make lean` green before
and after, the 232-declaration set byte-identical):

- **Operation order corrected.** `add`/`sub`/`neg`/`smul` now precede `mul`/`wedge`/`dot` in all
  three files — a student meets addition before multiplication (§1.3 before §1.4).
- **The algebra laws now live with their algebra.** The former `AlgebraLaws.lean` folded into
  `G2.lean` and `G3.lean` (each gained an `### The algebra laws` section); `G1.lean` already kept
  its `mul_comm`/`mul_assoc`/`one_mul`/`mul_add` inline. `AlgebraLaws.lean` is gone.

The reorder is recorded in `tasks/archive/2026/10/29/reorder-gn-lean-to-teaching-order.md`.

### Caveats — where a deviation from the teaching order is legitimate

Worth stating, because "mirror the textbook" is a default, not a mandate (the maintainer
asked to hear why some things should stay separate):

- **Lean's dependency order can force a local reversal.** A proof may need a lemma about
  `mul` to state a fact filed under `add`; the *dependency* wins over the pedagogical
  order where they conflict. Note each such reversal in a comment.
- **Cross-algebra shared facts may justify a shared file.** A fact that genuinely needs
  machinery from a *later* module cannot move *up* into `G2.lean` without creating an
  import cycle — that would be a real reason to leave it separate. In the event, none did:
  the 2026-10-29 reorder's delete-and-rebuild confirmed every `G2`/`G3` law's dependencies
  are satisfied within its own algebra, so all of `AlgebraLaws.lean` folded in with no cycle.
  (The one suspected obstacle — `AlgebraLaws.lean`'s `import GacalcProofs.Versor2D`, with
  `Versor2D` importing `G2` — was a **stale import** naming no `Versor2D` symbol, so it
  blocked nothing; it vanished with the file.)
- **The representation/plumbing block** (the coordinate `structure`, `zero`/`one`, basis
  blades, `ext`) is prerequisite scaffolding with no textbook analogue; it legitimately
  comes first, before "addition," the way a chapter sets notation before teaching.
