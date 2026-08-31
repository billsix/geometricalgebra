# Grassmann absolute/relative units — concept, citation, and runtime tests

**Status:** blocked — citation and definitions OBTAINED 2026-08-31 (see below); still gated on the
maintainer confirming the interpretation and choosing the predicate/tests.
**Priority:** 7
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer confirms the proposed interpretation (absolute unit = the scalar 1, NOT
`1*e_1`) and decides what predicate/tests to build.
**Recheck:** the remaining Open questions below are answered (maintainer-gated; `/recheck-blocked`
surfaces it).

## The citation and quote (provided by the maintainer, 2026-08-31)

**Hermann Grassmann, *Extension Theory* (Ausdehnungslehre, 1862), trans. Lloyd C. Kannenberg,
AMS History of Mathematics vol. 19, p. 3:**

> "I define as a unit any magnitude that can serve for the numerical derivation of a series of
> magnitudes, and in particular I call such a unit an original unit if it is not derivable from
> another unit. The unit of numbers, that is one, I call the absolute unit, all others relative.
> Zero can never be a unit."

## Proposed interpretation (agent, 2026-08-31 — NOT yet confirmed by the maintainer)

**The full explanation as given to the maintainer, kept here verbatim-in-substance so the
eventual reference doc can be distilled from it once confirmed.**

### The vocabulary

*Magnitude* (Größe) is Grassmann's word for **quantity in general** — numbers included (the
maintainer's hunch "magnitude ≈ vector" is close but broader). What we call a vector is his
*extensive magnitude of the first step*: "any expression derived from a system of units by
numbers", the coefficients being the "derivation numbers". In `3*e_1 + 4*e_2`, the 3 and 4 are
derivation numbers and the whole expression is an extensive magnitude.

### The p. 3 sentence, unpacked

- **"A unit is any magnitude that can serve for the numerical derivation of a series of
  magnitudes."** A unit is a *role you give something*, not a property it has: adopt a magnitude
  `u`, then "numerically derive a series" from it — its multiples `2u, ½u, −3u, …`. Anything
  nonzero can play the role.
- **"Zero can never be a unit"** — every multiple of zero is zero; no series comes out.
- **"The unit of numbers, that is one, I call the absolute unit, all others relative."** The
  absolute unit is **the number 1** (gacalc's `one`) — the one unit nobody *chooses*: arithmetic
  hands it to you, everyone's 1 is the same. Every other unit (a meter, a corn flake, `e_1`)
  exists only because someone adopted it within some system, and is meaningful only *relative to*
  that choice. Absolute/relative = canonical-versus-chosen, NOT scalar-versus-vector.
- **"An original unit is one not derivable from another unit."** Among relative units, the
  *original* ones are the primitively posited generators (`e_1, e_2, e_3`); units built from them
  (the higher-step units `e_1 e_2`, `e_1 e_2 e_3`, as products of original units) are *derived*
  units.

### The classification table

| thing | Grassmann's category |
|---|---|
| `1` (the scalar, gacalc's `one`) | **the absolute unit** (unique) |
| `e_1`, `e_2`, `e_3` | **original relative units** |
| `e_12`, `e_123` | derived (relative) units — products of original units |
| `3*e_1 + 4*e_2`, `e_1 + e_2` | not units of the adopted system — **derived extensive magnitudes** (adoptable as derived relative units of another system) |
| `0` | never a unit |

### The corn-flake walkthrough (maintainer's example, 2026-08-31)

A corn flake, taken as the thing you count, is a unit: it numerically derives the series
2 flakes, 3 flakes, half a flake. It is not the number 1, so it is a **relative unit** — and an
*original* one in a one-dimensional flake-counting system, since it is posited directly. Switch
systems: let `e_1` = one calorie and `e_2` = one mg of sodium (two original units of a nutrition
system). The *same* corn flake, re-expressed there, is `4*e_1 + 2*e_2` — a **derived magnitude**
of that system, derivation numbers 4 and 2. It can still be adopted as a unit ("how many flakes'
worth of nutrition is this bowl?" is numerical derivation from it) — but then it is a *derived*
relative unit, not an original one, because it is built from the calorie and sodium units. Same
flake, three classifications, depending on the adopted system: that system-dependence is exactly
what "relative" means, and only 1 escapes it.

### Sources (secondary literature corroborating the reading)

- Cantù, "Grassmann's epistemology: multiplication and constructivism" —
  https://philarchive.org/archive/CANGEM
- "From Grassmann complements to Hodge-duality" — https://arxiv.org/pdf/2003.10728
- "Grassmann's Concept Structuralism", *The Prehistory of Mathematical Structuralism* (OUP) —
  https://academic.oup.com/book/41041/chapter/349347436
- The translation itself: AMS HMATH 19 — https://bookstore.ams.org/hmath-19/

### Summary of the reading

Corroborated against secondary literature on the 1862 text (Cantù, "Grassmann's epistemology";
the Hodge-duality history in arXiv:2003.10728): Grassmann's *extensive magnitude* is "any
expression derived from a system of units … by numbers", the coefficients are "derivation
numbers", and numbers themselves are the extensive magnitudes over the system consisting of the
absolute unit alone.

- **Magnitude** (Größe) = quantity in general (numbers included); an *extensive magnitude of the
  first step* is today's vector.
- **Unit** = a role, not an intrinsic property: any magnitude you adopt as a generator, whose
  scalar multiples ("numerical derivation of a series") you then form. Zero is excluded because
  its multiples are all zero — no series.
- **Absolute unit** = **the number 1** — the one unit that is canonical rather than chosen
  (gacalc's `one` / `Scalar(1)`). **NOT `1*e_1`** — this contradicts the task's original working
  example, flagged for the maintainer.
- **Relative units** = every adopted unit other than 1 (a meter, a corn flake, `e_1`) — "relative"
  because they exist only relative to a chosen system of units.
- **Original unit** = a relative unit posited primitively, not derived from other units: the
  basis vectors `e_1, e_2, …`. Higher-step units (`e_12`, `e_123`) are *derived* units (products
  of original units); `3*e_1 + 4*e_2` is not a unit of the standard system at all but a **derived
  extensive magnitude** — though it can be *adopted* as a (relative, non-original) unit of
  another system.
- The maintainer's corn-flake example (2026-08-31): a corn flake counted as itself is an original
  relative unit of a 1-D system; the same flake re-expressed as its nutrition vector
  `4*e_1 + 2*e_2` (calories, sodium) is a derived magnitude of the {calorie, sodium} system —
  adoptable as a derived relative unit there.
- The originally-named third category "**reference**" does not appear in the quote; likely the
  memory was of the *system of units* a relative unit is relative to (open question below).

## Goal

Maintainer's idea, verbatim: *"Make run time tests for absolute unit, relative unit, reference. The
original guys work from the 1800s, ask me about the book name, author, and page number, and then do.
1 * e_1 is an absolute unit. a relative unit is 3 * e_1 + 4 * e_2. the base types with a coefficient of
1 are absolute units. but, ask for me the definition from the book, I think by Grassmann."*

Introduce the absolute-unit / relative-unit / reference concepts (from the 1800s source), and add
runtime tests for them.

## Context (investigation 2026-08-27)

- **Genuine gap** — no reference doc or code mentions "absolute unit"/"relative unit"/Grassmann's
  terminology (confirmed by repeated greps across active/reference/archive).
- The only adjacent work is display convention: `2026/08/26/explicit-unit-coefficients.md` made
  `e_1` render as `1*e_1` (~235 sites) — that's *display*, not the Grassmann *concept* or tests for it.
- The maintainer's own examples: `1*e_1` = absolute unit; `3*e_1 + 4*e_2` = relative unit; "base types
  with coefficient 1 are absolute units." A third category, "reference," is named but not defined.

## Plan

- [x] Get the exact 1800s citation and definitions — obtained 2026-08-31 (quote above).
- [ ] Maintainer confirms (or corrects) the proposed interpretation and answers the open
      questions below — **deliberately deferred by the maintainer 2026-08-31 ("I'll deal with
      this later"); do not re-raise unprompted.**
- [ ] Distill the confirmed interpretation into `tasks/reference/grassmann-units.md` (the
      taxonomy, table, corn-flake example, citation, sources).
- [ ] Ship whatever Open question 3's answer selects (reference doc only / + taxonomy-as-tests /
      + public predicates).

## Open questions

1. ~~**Citation**~~ — ANSWERED 2026-08-31: Grassmann, *Extension Theory*, trans. Kannenberg, AMS
   History of Mathematics vol. 19, p. 3 (quote recorded above).
2. **Interpretation** — does the maintainer accept the proposed reading above, in particular that
   the **absolute unit is the scalar 1, not `1*e_1`** (which corrects the task's original working
   example)?
3. **Predicate** — given that reading, what should ship: (a) a reference doc only (the taxonomy is
   about *roles* in a chosen system, so a runtime predicate is of limited meaning beyond
   `is_absolute_unit()` ≡ `== one`); (b) reference doc + tests that *encode the taxonomy as
   assertions on examples* (absolute: `one`; original relative: `1*e_1`; derived units: `e_12`;
   derived magnitudes: `3*e_1 + 4*e_2`; zero excluded); or (c) also public predicates
   (`is_absolute_unit`, `is_original_unit`)?
4. **"Reference"** — the third category originally named: was it the *system of units* (the thing
   relative units are relative to), or something else in the book?
