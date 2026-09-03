# Q79 eta9 Cayley critical correlated-readout theorem

**Identifier:** CBF.T67

**Status:** same-source characteristic-zero scalar and first jet certified

**Physical status:** the calculation is attached to the already declared
method branch; it does not select the physical q79 endpoint

## Purpose

CBF.T66 proves the exact characteristic-zero inverse and verifies every value
and derivative relation row, but its independent-coordinate readout loses the
correlations responsible for cancellation. T67 computes the scalar directly
from the common geometric source and therefore tests the actual denominator
without pretending that 6,777 dependent coordinates vary independently.

## Signed source representation

Each high-precision source object is exported as

```text
exact object in center + signed correction + tail disk.
```

The signed correction captures the component discarded by the first
binary64 center. The remaining nonnegative tail contains only the genuine
forward uncertainty and the second conversion remainder. For the common
H4-T141 top source, the maximum tails are

```text
value       1.617226186017182e-33,
derivative  1.456934916273624e-24.
```

The earlier value radius of about `2.80e-17` was principally a center-export
width, not geometric uncertainty. Treating it as an independent physical
radius was the source of the false denominator obstruction.

The same representation is used for `A`, `C`, `B`, `B'`, the toric Jacobian
`J`, its derivative `J'`, and the pivot data. Their hashes and support unions
are frozen in the two signed-source certificate directories.

## Common-source Cayley transport

The 2,584 pivot anchors are related to one top source by the exact sparse map

```text
p  = L top,
p' = L top'.
```

Here `L=I-N`, the diagonal is one and `N^2=0`. Consequently the map is exactly
invertible with inverse `I+N`; no numerical gauge is selected. This identity
is also checked directly against every promoted pivot center.

## Correlated adjoint contraction

Write the reduced value and derivative systems as

```text
A x  = B p,
A x' = B p' + B' p + C x.
```

Let `g` and `g'` be the free-coordinate toric-Jacobian rows. Solve the two
adjoint systems

```text
A^T z = g,
A^T y = g' + C^T z.
```

Then define the pivot readout rows

```text
K  = J_P  + B^T z,
K' = J'_P + B'^T z + B^T y.
```

Because `p=L top`, the final common-source rows are `L^T K` and `L^T K'`.
With exact adjoints this gives

```text
D  = (L^T K)^T top,
D' = (L^T K)^T top' + (L^T K')^T top.
```

The implementation uses ten 512-bit Arb residual refinements for the value,
derivative and both adjoint systems. Nonzero adjoint residuals are retained as
the rigorous remainder terms `r_z^T x` and `r_y^T x`; they are not dropped.
The T66 Neumann inverse bound supplies the forward-error enclosure.

## Certified result

The toric-Jacobian denominator and first path derivative are

```text
D = 3.546101021348808e-05
    + 1.795488342992707e-04 i,
error(D) <= 1.671626130599143e-20,
|D| >= 1.830171225420945e-04,

D' = -7.201503518702864e-04
     + 8.723385313448658e-04 i,
error(D') <= 1.195484433400900e-13,
|D'| >= 1.131190099982028e-03.
```

Both disks exclude zero. T64's exact normalization formula therefore gives

```text
s_C  = 585/(2D)
     = 309666.0027514012 - 1567924.023635981 i,
error(s_C) <= 1.459760392727150e-10,

s_C' = -(585/2) D'/D^2
     = -8712642.17150278 + 4654975.173896328 i,
error(s_C') <= 1.043967793093987e-03.
```

The relative error upper bound for `s_C` is
`9.133714416336445e-17`.

An independent verifier reconstructs the common-source contractions solely
from the emitted arrays. Coordinatewise binary64 export is cancellation
sensitive, so it checks interval-disk containment rather than requiring the
exported midpoint dot product to equal the internal Arb midpoint. Its more
conservative disks still give

```text
independent |D| lower   1.811323e-04,
independent |D'| lower  1.059661e-03.
```

## Theorem

For the declared edge-2, `t=1/2`, lift-sign `-1`, seed-7909 method branch:

1. The common characteristic-zero value and first jet exist uniquely by T66.
2. Exact Cayley transport expresses all pivot sources through one top source.
3. The correlated toric-Jacobian denominator and derivative both exclude
   zero.
4. The canonical Serre scale and its first path derivative are the disks
   displayed above.
5. The result uses zero observed values, zero new continuous fit parameters
   and zero new discrete fit selectors.

## Scope boundary

T67 closes the characteristic-zero scalar-execution clause left by T65 and
T66. It does not prove that this B89 method member is the physical q79 HYM
endpoint, that `beta_C` vanishes, that a selected physical meridian has been
executed, or that any resulting quantity agrees with an observed Standard
Model value. Those are mathematically distinct selection and period-readout
claims.

## Reproducibility

The result packet is
`q79_eta9_cayley_critical_correlated_readout.packet.json`. Its 15 bound arrays
are hash-bound beside it. The signed sources live in
`certificates/q79_eta9_cayley_critical_signed_correction_seed7909/` and
`certificates/q79_eta9_cayley_top_signed_source_seed7909/`. The independent
verifier is `verify_q79_eta9_cayley_critical_correlated_readout.py`.

The top-source constructor replays H4-T141 from the adjacent preprojection
repository to recover pre-conversion Arb centers. Once emitted, the frozen
certificate and T67 verifier are portable and do not require that sibling
repository.

The independent Kernel execution was job
`cb11a3cd-4849-4fe8-aab0-9521663812c2`. Its input capsule SHA-256 is
`520b23f484d4b62203feb5f3d8d0f49cb7025e0711f81f95fd689ce104a195d5` and
its 15-file result capsule SHA-256 is
`f9649a21bd670b9cdb7853f09ea3a0d5c5a77c7ef863b0f5479c6eb352dabdbd`.
The committed packet differs from the archived result packet only by
repo-relative provenance rebinding and the corresponding canonical hashes;
the 14 numerical arrays are unchanged.
