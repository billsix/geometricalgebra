# Why `I_r² = (−1)^(r(r−1)/2)` — the pseudoscalar-square sign, by counting flips

**Reference document** — a from-scratch, hand-countable proof that the r-dimensional unit
pseudoscalar squares to `(−1)^(r(r−1)/2)` in Euclidean 𝒢ₙ. Written for a high-school / early-college
reader: we work it out by hand for grades 1–5, watching every swap, then prove the general case two
ways (a short induction, then a one-line "reversal" argument). Durable domain + design notes; **update
in place**, not archived. Last updated 2026-08-16 (William Emerison Six <billsix@gmail.com>). Supports
`base.pseudoscalar_squared_sign` and the task
`tasks/prove-blade-square-sign-equals-pseudoscalar-squared.md`; the permanent check is
`tests/test_pseudoscalar_square_sign.py`.

## What we're proving, and why anyone cares

The **unit pseudoscalar** of the n-dimensional algebra is the product of all n basis vectors, in
order:

>   `I_r  =  e_1 e_2 … e_r`.

(We use `r` for its grade so the formula reads the same whether it's the top blade of the whole
algebra or an r-blade sitting inside a bigger one.) The claim is:

>   **`I_r²  =  (−1)^(r(r−1)/2)`**   (Euclidean signature: every `e_i e_i = +1`).

This one sign controls real code. `reverse()` gives the grade-r part of a multivector exactly this
sign (Hestenes & Sobczyk eq. 1.19), `exp()` uses it to decide whether a blade squares to a positive
or negative number, and the code generator bakes it into every generated `reverse()`. In the library
it's the helper `base.pseudoscalar_squared_sign(r)`. So "what is the sign of `I_r²`?" is a question
the code asks constantly — and the answer is a formula you can verify by hand.

## The only three rules we need

Everything below is just these, applied over and over (the same rules the notebook
`displaymv.py` teaches and that `gn.py`'s `decrease_grade` implements):

- **R1 — a basis vector squares to one:** `e_i e_i = +1`. *(This is where "Euclidean" lives; with a
  different signature it could be −1, and the proof still goes through — see the last section.)*
- **R2 — swapping two *different* neighbours flips the sign:** `e_i e_j = − e_j e_i` for `i ≠ j`.
- **Concatenation:** writing blades next to each other just concatenates their index lists, and
  multiplication distributes over `+`. (We never need distributivity here — `I_r` is a single blade.)

We'll call R2 a **swap** (or **flip**) and R1 an **annihilation** (a pair vanishes, leaving `+1`).
Counting swaps is the whole game: each swap multiplies our running sign by `−1`, and an annihilation
changes nothing but the length.

## Do it by hand: grades 1 through 5

The strategy every time: write `I_r²` out as two identical blocks, then take the **first vector of the
second block** and slide it left, one swap at a time, until it meets its twin in the first block and
annihilates. What's left is the *same problem one grade smaller* — so we just repeat.

### Grade 1 — `I_1 = e_1`

```
I_1² =  e1 e1              sign = +1
        └──┘  e1 e1 = +1   (annihilate, R1)
     =  +1
```
Zero swaps. **`I_1² = +1`.**

### Grade 2 — `I_2 = e_1 e_2`

```
I_2² =  e1 e2 e1 e2                    sign = +1
              ^^ slide this e1 left
        e1 e1 e2 e2   (past e2)   R2 → 1 swap,  sign = −1
        └──┘ e1 e1 = +1     └──┘ e2 e2 = +1     (annihilate)
     =  −1
```
One swap. **`I_2² = −1`.**  (This is the famous "`i² = −1`" of the plane's unit bivector.)

### Grade 3 — `I_3 = e_1 e_2 e_3`

```
I_3² =  e1 e2 e3 · e1 e2 e3                 sign = +1
                   ^^ slide this e1 left
        e1 e2 e1 e3 · e2 e3   (past e3)  R2 → sign = −1
        e1 e1 e2 e3 · e2 e3   (past e2)  R2 → sign = +1
        └──┘ e1 e1 = +1                       (annihilate)
              e2 e3 · e2 e3                 ← the SAME shape, one grade smaller (indices {2,3})
                     ^^ slide this e2 left
              e2 e2 e3 · e3   (past e3)   R2 → sign = −1
              └──┘ e2 e2 = +1  └──┘ e3 e3 = +1
     =  −1
```
Swaps: `2 + 1 + 0 = 3`. **`I_3² = −1`.**

### Grades 4 and 5 — count the peels

By now the pattern is clear, so instead of every single swap we count **per peel**: sliding the lead
vector of the second block into its twin costs `(current grade − 1)` swaps, then the problem drops one
grade. Each row below is one peel.

```
I_4²:  peel e1 out of {1,2,3,4}   → 3 swaps,  reduces to {2,3,4}
       peel e2 out of {2,3,4}     → 2 swaps,  reduces to {3,4}
       peel e3 out of {3,4}       → 1 swap,   reduces to {4}
       peel e4 out of {4}         → 0 swaps,  done
       total swaps = 3 + 2 + 1 + 0 = 6   →   (−1)^6 = +1
```
**`I_4² = +1`.**

```
I_5²:  peel e1 → 4 swaps   (reduces {1,2,3,4,5} → {2,3,4,5})
       peel e2 → 3 swaps
       peel e3 → 2 swaps
       peel e4 → 1 swap
       peel e5 → 0 swaps
       total swaps = 4 + 3 + 2 + 1 + 0 = 10   →   (−1)^10 = +1
```
**`I_5² = +1`.**

### The tally

| grade `r` | swaps to canonicalize | `= r(r−1)/2`? | `I_r² = (−1)^swaps` |
|:---:|:---:|:---:|:---:|
| 1 | `0`                     | `0`  | `+1` |
| 2 | `1`                     | `1`  | `−1` |
| 3 | `2+1+0 = 3`             | `3`  | `−1` |
| 4 | `3+2+1+0 = 6`           | `6`  | `+1` |
| 5 | `4+3+2+1+0 = 10`        | `10` | `+1` |

Two things jump out:

1. **The swap total is always a triangular number.** Peeling grade `r` costs
   `(r−1) + (r−2) + … + 1 + 0`, and that sum is `r(r−1)/2` — the number of ways to pick 2 of the `r`
   vectors, `C(r,2)`. So the exponent in `(−1)^(swaps)` is exactly `r(r−1)/2`.
2. **The signs march in a period-4 pattern** `+, −, −, +, +, −, −, +, …`. That's because
   `(−1)^(r(r−1)/2)` is `+1` when `r ≡ 0 or 1 (mod 4)` and `−1` when `r ≡ 2 or 3 (mod 4)` — the
   triangular number is even, then odd twice, then even twice, forever.

## Route A — the induction (this is the hand method, made airtight)

The peeling above *is* an induction. Let `s(r)` be the sign of `I_r²`.

- **Base case:** `s(0) = +1` (the empty product `I_0 = 1`, and `1² = 1`); equivalently `s(1) = e_1 e_1 = +1`.
- **Inductive step:** in `I_r² = (e_1 … e_r)(e_1 … e_r)`, slide the second block's `e_1` left past
  `e_r, e_{r−1}, …, e_2` — that's `r − 1` swaps by R2, since all those vectors differ from `e_1`.
  Now the two `e_1`s are adjacent; annihilate with R1. What remains is `e_2 … e_r e_2 … e_r`, which is
  `I'²` for the algebra on indices `{2, …, r}`. Relabelling `2→1, 3→2, …` doesn't change any product
  (the rules never mention *which* index, only whether two are equal), so that leftover squares with
  sign `s(r−1)`. Therefore

  >   `s(r) = (−1)^(r−1) · s(r−1)`.

Unrolling from the base:

>   `s(r) = (−1)^((r−1) + (r−2) + … + 1 + 0) = (−1)^(r(r−1)/2)`.   ∎

That exponent sum is the same triangular number we counted by hand. The induction is nothing more than
"peel one pair, recurse," written once and for all.

## Route B — the slick one-liner (via `reverse`)

There's an even shorter argument, and it's worth seeing because it connects directly to `reverse()`.

The **reverse** of `I_r` writes its factors back-to-front:

>   `Ĩ_r = e_r e_{r−1} … e_1`.

Turning `e_1 e_2 … e_r` into `e_r … e_2 e_1` by adjacent swaps takes `C(r,2) = r(r−1)/2` swaps (that's
how many out-of-order pairs a full reversal has), each an R2 flip, so

>   `Ĩ_r = (−1)^(r(r−1)/2) · I_r`.     (★)

Separately, `I_r Ĩ_r` **telescopes to `+1`**: line them up and cancel from the middle out —
`e_1 … e_r · e_r … e_1`, the inner `e_r e_r = +1` (R1) disappears, then `e_{r−1} e_{r−1} = +1`, and so
on down to the last `e_1 e_1 = +1`:

>   `I_r Ĩ_r = +1`.     (this is exactly what makes `I_r` a *unit* pseudoscalar)

Now multiply. From (★), `I_r = (−1)^(r(r−1)/2) Ĩ_r` (a sign is its own inverse), so

>   `I_r² = I_r · I_r = (−1)^(r(r−1)/2) · (I_r Ĩ_r) = (−1)^(r(r−1)/2) · 1 = (−1)^(r(r−1)/2)`.   ∎

Both routes land on the same formula. Route A shows *why* by counting; Route B shows that the sign is
literally the **reversion sign** — which is why the library's helper serves both `reverse()` and the
square of the pseudoscalar with one function.

## In the code

- **`base.pseudoscalar_squared_sign(r)`** returns this `±1`. As of Phase 1 it computes it the slow,
  obviously-correct way — it *actually squares* the r-dimensional unit pseudoscalar
  (`Gn.unit_pseudoscalar_squared(r).scalar_part()`) — deliberately, so the code matched a fact before
  we optimized. The Phase-2 change (see the task) swaps in the proven closed form
  `(-1) ** ((r * (r - 1)) // 2)`, keeping the slow line as a comment so a reader sees they're the same
  calculation.
- **Callers:** `Gn.reverse()` and `exp()` call it per use; the generator evaluates it at code-gen time
  and bakes a constant `±1` into each generated `reverse()`, so the specialized classes pay nothing at
  runtime either way.
- **The permanent check:** `tests/test_pseudoscalar_square_sign.py` asserts, over `r = 0..N`, that the
  *independent* squaring `Gn.unit_pseudoscalar_squared(r).scalar_part()` equals the closed form
  `(−1)^(r(r−1)/2)`. Because it re-squares the pseudoscalar rather than re-deriving the formula, it
  keeps guarding the equivalence even after Phase 2 makes the helper *be* the closed form.

## Signature note (why "Euclidean" was the only assumption)

R1 (`e_i e_i = +1`) is the sole place the Euclidean signature entered — and only through the *final*
annihilation of each pair, never through a swap. If instead `e_i e_i = ±1` (a mixed signature), every
step of both proofs is unchanged except that each annihilation contributes its own `±1` rather than
`+1`; the swap-counting `(−1)^(r(r−1)/2)` factor is identical. gacalc hardcodes `+1`, so we state the
clean Euclidean result. (See `tasks/reference/design-decisions.md` for the hardcoded-signature
decision.)

## Related

- `tasks/prove-blade-square-sign-equals-pseudoscalar-squared.md` — the task this doc proves (Phase 2).
- The associativity write-up in `tasks/prove-associativity-of-multiplication.md` uses the same
  swap/annihilate machinery (`decrease_grade`) for a different theorem.
- `notebooks/displaymv.py` — the plain-language intro to the three rules, for a reader meeting them
  for the first time.
