# Q79 eta9 directed Cayley-Serre scale theorem

**Identifier:** CBF.T65

**Status:** exact finite/topological reduction closed; frozen-binary value promotion rejected

**Physical status:** no eta9 scale, derivative, period, or beta value is promoted

## Purpose

CBF.T64 proves the intrinsic family-wide normalization formula

```text
s_C=(585/2) f_crit(M m_1494) / f_crit(J_toric).
```

H4-T141 independently supplies directed characteristic-zero balls for the
projective top functional and its first path derivative. The missing step is
to extend that functional through the 9,361-dimensional Cayley critical
degree and evaluate the denominator without introducing a row-selection
gauge or an empirical normalization.

This theorem performs the exact reduction and tests the first proposed
numerical execution. The test rejects promotion from frozen binary64
coefficients. It thereby prevents a numerically precise but gauge-dependent
number from being mistaken for an MTT-selected value.

## Exact reduction

At the T64 good reduction over `GF(21817)`, streaming the 16,740 original Cox
relation rows selects 9,360 independent rows in 9,361 columns. The quotient
therefore has dimension one. This is an exact finite-field rank certificate;
it is not used as a complex inverse estimate.

Multiplication by the Cox monomial and the determinant-one regularizing gauge
give an exact embedding

```text
E_M : C^9361 -> C^2584.
```

Its 2,584 pivot columns are distinct and it has no support on the remaining
6,777 columns. Consequently the H4-T141 top functional fixes 2,584 critical
coordinates and leaves a `13014 x 6777` reduced complex relation system. This
is the correct dimensional reduction for the value and derivative equations

```text
R f = 0,                  E_M f = f_top,
R f' = -R' f,             E_M f' = f'_top.
```

## Predeclared row-gauge test

Three seeded rank-revealing selections were made before inspecting their
scale values:

```text
seed 7909
seed 7919
seed 7933
```

Each selects 6,777 distinct original relation rows and has a complete sparse
binary64 LU. For each selection, all matrix and right-side coefficients were
then frozen as exact dyadic numbers and the solve was refined with 512-bit
Arb arithmetic. The maximum residual component is below `1e-80` in every
case.

Nevertheless, the resulting edge-2 scale midpoints are

```text
7909 : 293941.6521159965 - 1520172.9000020993 i
7919 : 341125.4178549821 - 1565714.4364540790 i
7933 : 326644.5767836265 - 1371357.0139603699 i
```

The smallest pairwise relative gap is approximately `4.09e-2`. Moreover,
the ordinary binary64 solve for seed 7909 differs materially from its own
exact-dyadic refinement. Solver residual is therefore not the source of the
cross-gauge disagreement. The frozen coefficients encode slightly different
systems, and their severe conditioning amplifies those differences.

## Theorem

For the selected framed member and edge-2 midpoint:

1. The exact good-reduction critical quotient has dimension one.
2. The Cayley top embedding fixes 2,584 coordinates and leaves exactly 6,777
   extension coordinates.
3. Three predeclared full-rank binary row gauges admit residual-refined dyadic
   solves.
4. Those solves fail row-gauge stability by more than one percent.
5. Therefore no scale or derivative obtained from the frozen-binary
   coefficient systems is admissible for theorem or physical promotion.

Item 5 is a rejection of a numerical method, not a no-go theorem for the
characteristic-zero geometric functional. In particular, T64's formula and
H4-T141's directed top trace remain valid at their declared tiers.

## Required exit

The next admissible computation must use one common characteristic-zero
coefficient-ball system. It must:

1. enclose every selected critical coefficient and top anchor;
2. certify a `6777 x 6777` inverse with a strict Neumann bound;
3. solve value and derivative equations with forward-error balls;
4. verify all 13,014 nonzero reduced relation rows, not only the selected
   minor;
5. exclude zero from the toric-Jacobian denominator ball before forming
   `s_C` and `s'_C`.

If the denominator ball contains zero or the Neumann bound is at least one,
the result is a certified conditioning obstruction and a new row gauge or
analytic preconditioner is required. If all five tests pass, the resulting
balls are row-gauge independent by uniqueness and may proceed to adaptive
path panels.

## Scope and parameters

No observed value, fit parameter, continuous selector, or discrete physical
selector enters this calculation. The framed B89 graph member remains a
method-validation member and is not promoted as the physical eta9 endpoint.
Nothing here decides `beta_C`, `U_eta9`, the physical meridian, or the final
248-row period readout.

## Reproducibility

The controlling packet is
`q79_eta9_directed_cayley_serre_scale.packet.json`. The independent verifier
is `verify_q79_eta9_directed_cayley_serre_scale.py`. The three portable
refinement inputs live under
`certificates/q79_eta9_cayley_critical_refinement_seed*/`; each directory
contains its own selected-row array and is independent of Kernel scratch
paths.
