# The geometric product of `Gn`, by hand — slide, flip, annihilate

**Reference document** — a from-scratch, hand-countable account of how the geometric product works in
Euclidean 𝒢ₙ: write the two factors side by side, slide each vector left past its neighbours one swap
at a time (each a sign flip), annihilate equal neighbours (`eᵢeᵢ = +1`), and read off the canonical
blade and its sign. Written for a high-school / early-college reader, in the same count-every-move
voice as [[pseudoscalar-square-sign]] (`tasks/reference/pseudoscalar-square-sign.md`), which does the
special case `I_r²`. Durable domain + design notes; **update in place**, not archived. Last updated
2026-10-09 (William Emerison Six <billsix@gmail.com>). This is the general/reference form; the book's
`book/docs/blade-square-sign.rst` presents the blade-squaring slice of the same mechanism, and the
mechanism itself is `gn.py`'s `decrease_grade`. Every product below was checked against a `Gn` REPL.

## The only three rules we need

A **blade** is a product of basis vectors written next to each other, like `e_1 e_2` or `e_2 e_1 e_3`.
A general multivector is a sum of blades with number coefficients, like `3 * e_1 + 4 * e_2`. The whole
geometric product is these three rules, applied over and over (the same rules the notebook
`notebooks/displaymv.py` teaches and `gn.py`'s `decrease_grade` implements):

- **R1 — a basis vector squares to one:** `e_i e_i = +1`. *(This is where "Euclidean" lives.)*
- **R2 — swapping two *different* neighbours flips the sign:** `e_i e_j = − e_j e_i` for `i ≠ j`.
- **Concatenation + distributivity:** writing blades next to each other concatenates their index
  lists, and multiplication distributes over `+` (so `(a + b) * c = a*c + b*c`), with number
  coefficients sliding freely to the front (`(2 * e_1)(3 * e_3) = 6 * e_1 e_3`).

We call R2 a **swap** (or **flip**) and R1 an **annihilation** (a pair vanishes, leaving `+1`).
"Multiplying" is just: concatenate, then **canonicalize** — slide the indices into increasing order,
flipping the sign on every swap, and cancel any pair that meets. The canonical blade (indices strictly
increasing) plus the running sign is the answer.

## Watch the moves

### One swap — `e_2 * e_1`

```
e2 e1                 sign = +1
^^ ^^ out of order (2 > 1): swap them        R2 → 1 swap, sign = −1
e1 e2                 sign = −1
= −e1 e2   (= −e_12)
```
Out-of-order neighbours cost one flip. **`e_2 * e_1 = − e_1 e_2`**, while `e_1 * e_2 = + e_1 e_2` needs
no move at all. Order is the whole difference between `+` and `−`.

### Swap, then annihilate — `e_1 * e_2 * e_1`

```
e1 e2 e1              sign = +1
   ^^ ^^ slide the right e1 left past e2 (2 ≠ 1): swap   R2 → sign = −1
e1 e1 e2              sign = −1
└──┘ e1 e1 = +1   (annihilate, R1)
= − e2
```
One swap brings the two `e_1`s together; R1 annihilates them. **`e_1 * e_2 * e_1 = − e_2`** — a
grade-3-looking concatenation collapses to a single vector.

### Annihilate from the middle — `(e_1 e_3)(e_3 e_1)`

```
e1 e3 e3 e1           sign = +1
   └──┘ e3 e3 = +1    (annihilate the inner pair, R1)
e1 e1                 sign = +1
└──┘ e1 e1 = +1       (annihilate, R1)
= +1
```
No swaps needed — the equal indices are already neighbours. **`(e_1 e_3)(e_3 e_1) = +1`.** (The three
ways to parenthesize this — `((e_1 e_3) e_3) e_1`, `e_1 ((e_3 e_3) e_1)`, `e_1 (e_3 (e_3 e_1))` — all
give `+1`; that products do not care about grouping is exactly *associativity*, proved the same way in
[[geometric-product-associativity]] (`tasks/reference/geometric-product-associativity.md`).)

### Coefficients come along for the ride — `(2 e_1)(3 e_3)(4 e_3)(5 e_1)`

```
(2*3*4*5) · e1 e3 e3 e1          sign = +1,  number = 120
120 ·      e1 e3 e3 e1
              └──┘ e3 e3 = +1    (annihilate)
120 ·      e1 e1
           └──┘ e1 e1 = +1       (annihilate)
= 120
```
The numbers multiply out front (`2*3*4*5 = 120`); the basis vectors canonicalize on their own. **Result
`120`.** A scalar is a grade-0 blade — the empty product of basis vectors.

### Distribute, and watch the cross terms cancel — `(3 e_1 + 4 e_2)²`

```
(3 e1 + 4 e2)(3 e1 + 4 e2)
  = 9 (e1 e1) + 12 (e1 e2) + 12 (e2 e1) + 16 (e2 e2)        distribute
  = 9 (+1)    + 12 (e1 e2) + 12 (−e1 e2) + 16 (+1)          R1 on the squares, R2 on e2 e1
  = 9 + 16 + (12 − 12) e1 e2
  = 25
```
The two cross terms are equal and opposite — `e_1 e_2` and `e_2 e_1 = − e_1 e_2` — so they cancel,
and what survives is `9 + 16 = 25 = 3² + 4²`. **A vector times itself is its length squared** (the
Pythagorean sum), because every cross term pairs with its sign-flipped twin. **`(3 e_1 + 4 e_2)² = 25`.**

### Put it in order — `e_3 * e_1 * e_2`

```
e3 e1 e2              sign = +1
^^ ^^ 3 > 1: swap                 R2 → sign = −1
e1 e3 e2
   ^^ ^^ 3 > 2: swap              R2 → sign = +1
e1 e2 e3              sign = +1
= + e1 e2 e3   (= + e_123)
```
Two swaps slide `e_3` back to where it belongs; two flips make `+1`. **`e_3 * e_1 * e_2 = + e_123`.**

## The ASCII *is* `decrease_grade`

`gn.py`'s `decrease_grade` canonicalizes one concatenated blade by looking at the first two indices
`(a, c)` and doing exactly the moves above. Its four `match` arms are the four things that can happen:

| arm | pattern | what it is | the move above |
|---|---|---|---|
| **base** | `()` or `(_,)` | a scalar or single vector is already canonical | nothing to do |
| **annihilate** | `(a, c, …) if a == c` | `e_a e_a = +1`; drop the pair, keep the coefficient | R1 (the `└──┘` cancels) |
| **swap + negate** | `(a, c, …) if a > c` | out of order; swap to `(c, a, …)` and negate | R2 (the `^^ ^^` flip) |
| **in-order insert** | `(a, c, …) if a < c` | canonicalize the tail, then slide `a` into its place | R2 repeated until `a` lands |

So the diagrams are not a metaphor for the code — they are a trace of it. The running sign in the
ASCII is the coefficient's sign the function carries through the recursion; an annihilation is the
`a == c` arm; a flip is the `a > c` arm; "slide into order" is the `a < c` arm recursing. The product
of two multivectors is then just this applied to every pair of blades from the two factors and summed
(distributivity), which is the comprehension at the bottom of `Gn._geometric_product`.

## Where this leads

Two proofs reuse exactly this slide-flip-annihilate machinery, and reading them after this is the
natural next step:

- [[pseudoscalar-square-sign]] (`tasks/reference/pseudoscalar-square-sign.md`) — the special case
  `I_r² = (−1)^(r(r−1)/2)`, counting the swaps it takes to canonicalize `I_r` against itself.
- [[geometric-product-associativity]] (`tasks/reference/geometric-product-associativity.md`) — why the
  grouping never matters (the parenthesization aside under `(e_1 e_3)(e_3 e_1)` above, in general).

The permanent machine checks are the `Gn`/`G` conformance tests (`tests/test_conformance.py`,
`tests/test_multivector.py`) and the Lean product proofs in `proofs/GacalcProofs/`.
