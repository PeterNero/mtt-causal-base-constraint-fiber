# Q79 eta9 Cayley critical characteristic-zero extension theorem

**Identifier:** CBF.T66

**Status:** exact characteristic-zero inverse and all relation rows certified

**Physical status:** the endpoint, period readout, beta value and scale remain
unselected at this stage

## Purpose

CBF.T65 found the exact `2584+6777=9361` Cayley reduction but rejected three
frozen-binary row-gauge values. Small coefficient changes were amplified by a
severely conditioned selected minor. Residual refinement of those dyadic
systems could not establish the inverse or value of the intended
characteristic-zero operator.

T66 replaces that comparison by one interval problem. Its center, coefficient
radii, top anchors, first path derivative and all 16,740 original relation
rows come from the same selected edge-2, `t=1/2`, lift-sign `-1`, seed-7909
source.

## Strict inverse certificate

Let `A` be the exact `6777 x 6777` characteristic-zero selected operator and
let `P` be the sparse binary64 inverse used only as a preconditioner. The
required condition is

```text
eta = ||I-PA||_infinity < 1.
```

A coarse floating-point product overestimates 36 cancellation-sensitive rows.
Those rows are recomputed by embedding every binary64 midpoint as an exact
dyadic number in 512-bit Arb arithmetic and then adding the coefficient-ball
contribution. The remaining rows retain their outward-rounded coarse bounds.
The maximum final row is

```text
eta <= 0.484076176568743,
1-eta >= 0.515923823431257.
```

Hence the Neumann series converges and

```text
||A^(-1)||_infinity
 <= ||P||_infinity/(1-eta)
 <= 8.371141932383542e12.
```

This is a characteristic-zero interval statement. The finite-field rank from
T64 is used for combinatorial reduction, not as an inverse estimate.

## Value and first jet

The certified inverse bound is applied to the value equation and its first
path derivative,

```text
A x  = b,
A x' = b' + C x.
```

The midpoint residual, source uncertainty and coefficient action are bounded
separately. Substitution into the unreduced relation family gives:

```text
value rows enclosing zero       16740 / 16740,
derivative rows enclosing zero  16740 / 16740.
```

Thus the selected minor is not being mistaken for the complete equation: all
original rows are checked after the solve.

## Why the scale is not promoted here

T66 contracts independent coordinate radii against the toric-Jacobian row.
That discards the common-source correlation and produces a very wide valid
denominator disk containing zero. It is therefore forbidden to invert that
disk. This is an information-loss obstruction in the readout bound, not a
failure of the characteristic-zero inverse or relation equations.

## Theorem

Under the frozen source bindings in the T66 certificate:

1. The exact selected characteristic-zero Cayley minor is invertible.
2. Its value and first-derivative solutions are unique.
3. Their interval extensions satisfy all 16,740 original relation rows.
4. An independent-coordinate denominator bound does not exclude zero and no
   scale follows from T66 alone.

No observed value, continuous fit parameter, discrete fit selector or new
branch choice enters the result.

## Reproducibility

The portable source is
`certificates/q79_eta9_cayley_critical_characteristic_zero_seed7909/`.
The result packet is
`q79_eta9_cayley_critical_characteristic_zero_neumann.packet.json`, and the
independent verifier is
`verify_q79_eta9_cayley_critical_characteristic_zero_neumann.py`.

## Remaining frontier after T66

The immediate numerical task is to retain the same-source correlation through
the toric-Jacobian functional. Physical endpoint selection, the 248-row period
quotient, the detecting meridian and `beta_C` remain separate later tasks.
