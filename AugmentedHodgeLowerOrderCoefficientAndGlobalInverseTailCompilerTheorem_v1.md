# Augmented Hodge Lower-Order Coefficient and Global Inverse-Tail Compiler Theorem

**Identifier:** CBF.T59

**Date:** 2026-09-01

**Tier:** exact general coefficient theorem, exact five-degree weighted witness,
and exact conditional inverse/tail compiler

**Physical status:** the operator compiler is complete. The selected q79
visible-hidden HYM endpoint, its coefficient values and the inequalities needed
to accept its global inverse remain open.

## 1. Purpose

CBF.T58 gives the complete five-degree principal symbol and its exact pointwise
inverse. The earlier endpoint-Hilbert theorem proves abstractly that one
selected compact endpoint determines its adjoints and Galerkin matrices. The
missing bridge was an explicit formula for every lower-order coefficient and
a quantitative test that turns the T58 preconditioner into a projected global
inverse with a certified tail.

CBF.T59 supplies both. It also proves that lower-order matrix entries are not
independent source rows. They are derived from the same first-order
differential, connection, pairing and density.

## 2. Local coefficient theorem

Work in local orthonormal fiber frames and coordinates with positive Hilbert
density `mu(x) dx`. In degree `n`, write the selected augmented differential as

```text
L_n=A_n^j(x) partial_j+B_n(x).                    (2.1)
```

The maps outside degrees `-1,0,1,2,3` are zero. Define

```text
D_n=B_n^* - mu^(-1) partial_j(mu A_n^(j*)) .     (2.2)
```

Integration by parts gives

```text
L_n^*=-A_n^(j*) partial_j+D_n.                   (2.3)
```

The degree-`n` augmented Hodge operator

```text
Delta_n=L_n^*L_n+L_(n-1)L_(n-1)^*               (2.4)
```

has the ordered local expansion

```text
Delta_n=-C_n^(ij) partial_i partial_j
              +R_n^j partial_j+E_n,              (2.5)
```

where repeated coordinate indices are summed and

```text
C_n^(ij)=A_n^(i*)A_n^j
          +A_(n-1)^i A_(n-1)^(j*),              (2.6)

R_n^j=-A_n^(i*) partial_i A_n^j
      +D_n A_n^j-A_n^(j*)B_n
      -A_(n-1)^i partial_i A_(n-1)^(j*)
      +A_(n-1)^jD_(n-1)-B_(n-1)A_(n-1)^(j*),   (2.7)

E_n=-A_n^(i*) partial_i B_n+D_nB_n
    +A_(n-1)^i partial_iD_(n-1)
    +B_(n-1)D_(n-1).                            (2.8)
```

### Proof

Insert (2.3) into the two products in (2.4), apply the Leibniz rule once and
collect second-, first- and zero-order terms. Equations (2.6)-(2.8) are the
result. Since (2.3) is the Hilbert adjoint, the assembled operator is formally
self-adjoint. QED.

### Connection form

If a unitary covariant derivative is written locally as

```text
nabla_j=partial_j+Gamma_j,
L_n=a_n^j nabla_j+b_n,
```

then (2.1) holds with

```text
A_n^j=a_n^j,
B_n=b_n+a_n^j Gamma_j.                           (2.9)
```

Thus connection, curvature, torsion, Atiyah, anomaly and gauge-fixing terms
enter (2.7)-(2.8) through the selected `Gamma`, `b`, pairing and density. Once
those source fields are supplied, the coefficient arrays are outputs. Adding
independent numerical rows for `R_n` or `E_n` would duplicate source data.

In nonorthonormal fiber frames the same statement holds after local
orthonormalization, or with every star interpreted as the metric adjoint.

## 3. Exact five-degree weighted witness

The executable witness uses the exact T58 rank-four symbol maps at the real
covector `beta=(1,0,0)`. For every outgoing degree, set

```text
A_n(x)=g_n(x) a_n,
B_n(x)=f_n(x) a_n,                               (3.1)
```

with nonconstant rational linear polynomials `g_n,f_n` and density
`mu(x)=exp(x/3)`. Since the constant T58 maps satisfy
`a_(n+1)a_n=0`, the complete variable-coefficient differential still obeys

```text
L_(n+1)L_n=0.                                    (3.2)
```

The builder evaluates (2.6)-(2.8) in all five degrees and compares their
action against direct composition of `L_n`, `L_n^*`, `L_(n-1)` and
`L_(n-1)^*` on three dense polynomial probes per degree. All 15 identities
hold coefficient by coefficient over the rationals. At `x=0`, every second
order block reproduces the T58 Hodge symbol and projector ranks

```text
1,4,6,4,1.                                       (3.3)
```

This witness is nonphysical. Its role is to test derivative, density-drift,
incoming and outgoing terms exactly.

## 4. Projected global inverse theorem

Let `Pi` be the selected orthogonal kernel projector and work on
`(I-Pi)H`. Let `H_0` be the positive self-adjoint reference operator obtained
from the T58 principal preconditioner and a declared domain, with

```text
H_0 >= gamma I, gamma>0.                         (4.1)
```

Write the complete lower-order correction as a self-adjoint form perturbation
`K` and define

```text
S=H_0^(-1/2) K H_0^(-1/2),
eta=||S||.                                       (4.2)
```

If `eta<1`, then `H=H_0+K` is invertible on the projected complement and

```text
H^(-1)=H_0^(-1/2)(I+S)^(-1)H_0^(-1/2),         (4.3)
||H^(-1)|| <= 1/((1-eta)gamma).                  (4.4)
```

The order-`m` preconditioned Neumann approximation has certified remainder

```text
||H^(-1)-H_0^(-1/2)sum_(k=0)^m(-S)^kH_0^(-1/2)||
 <= eta^(m+1)/((1-eta)gamma).                   (4.5)
```

This follows from the geometric series for `(I+S)^(-1)`.

The exact rational witness uses `gamma=1`, a rank-one relative perturbation
with `eta=1/3`, and `m=4`. Its actual inverse error is `13/8100`, strictly
below the certified bound `1/162`.

## 5. Feshbach tail theorem

For a Galerkin projector `P` and tail `Q=I-P`, write

```text
H=[[A,B],[B^*,D]].                               (5.1)
```

If `D>=tau I`, `tau>0`, then the exact finite effective operator is

```text
F=A-BD^(-1)B^*.                                  (5.2)
```

If `A>=aI` and

```text
||B||^2/tau<a,                                   (5.3)
```

then `F` and `H` are positive and invertible. Their inverse is

```text
H^(-1)=
[[F^(-1),                 -F^(-1)BD^(-1)],
 [-D^(-1)B^*F^(-1),
  D^(-1)+D^(-1)B^*F^(-1)BD^(-1)]].             (5.4)
```

Replacing the operator norm by the Frobenius norm gives the executable
sufficient certificate

```text
a-||B||_F^2/tau>0.                               (5.5)
```

The rational witness verifies (5.2)-(5.5), the full block inverse and an
explicit one-dimensional kernel extension satisfying

```text
Delta G=G Delta=I-Pi,
Pi G=G Pi=0.                                     (5.6)
```

## 6. q79 execution contract

For q79 rank `102`, the five carrier dimensions remain

```text
1,105,309,307,102.                               (6.1)
```

The selected endpoint must emit only the geometric source fields needed to
form `A_n^j`, `B_n` and `mu`, together with the domain and kernel projector.
Equations (2.6)-(2.8) then emit all coefficient arrays. T58 supplies the
principal preconditioner. Equations (4.2) and (5.2) reduce global execution to
the numerical certificates

```text
gamma>0, eta<1, tau>0,
a-||B_tail||^2/tau>0,                            (6.2)
```

plus the requested finite-to-continuum intertwiner error.

The abstract compiler rows are therefore complete. Their selected numerical
values are not.

## 7. Physical boundary

CBF.T59 does not select:

- the characteristic-zero visible bundle or twisted hidden bundle;
- their common HYM chamber or connections;
- the q79 metric, density, torsion or lower-order arrays;
- the harmonic projector or physical spectral cutoff;
- numerical values of `gamma`, `eta`, `tau` or the Feshbach margin;
- a physical finite/continuum intertwiner or radii decision.

Accordingly `B.GEO.01` and `B.OP.01` remain open, and physical acceptance
remains `0/3` gates, `0/3` packets and `0/7` endpoint rows.

## 8. Parameter accounting

The theorem adds zero observed values, fitted values, continuous physical
parameters and discrete selectors. All rational quantities in the witnesses
are exactness fixtures only.

## 9. Reproduction

```powershell
python build_augmented_hodge_lower_order_inverse_tail_compiler.py
python verify_augmented_hodge_lower_order_inverse_tail_compiler.py
python -m unittest tests.test_augmented_hodge_lower_order_inverse_tail_compiler -v
```
