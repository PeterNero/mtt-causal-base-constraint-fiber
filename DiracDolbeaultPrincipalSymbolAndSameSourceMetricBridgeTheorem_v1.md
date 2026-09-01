# Dirac-Dolbeault Principal-Symbol and Same-Source Metric Bridge Theorem

**Identifier:** CBF.T56

**Date:** 2026-09-01

**Tier:** exact general theorem, exact source-locked benchmark and audited
conditional q79 composition

**Physical status:** the scalar-symbol obligation is derived from a supplied
Dirac/Dolbeault source. The selected physical q79 operator, density, HYM
connection, Green operator and continuum endpoint are not supplied here.

## 1. Purpose

CBF.T55 reconstructs the action scale, six-metric and full Hodge response from
the scalar positive principal symbol and oriented density of one upper action
Hessian. It correctly leaves open whether the selected q79 Hessian has that
operator class.

The present theorem removes scalarity as an independent source row whenever
the upper source emits a first-order Dirac-type closure charge. The chain is

```text
selected first-order charge B and its Hilbert density
  -> Clifford anticommutator
  -> scalar principal symbol of kappa B^2
  -> CBF.T55 metric/action-scale reconstruction
  -> CBF.T52 Hodge response.
```

This is distinct from CBF.T24 and CBF.T26. Those results concern a finite
graded tensor totalization and a finite 96-dimensional Dirac-square defect.
CBF.T56 concerns the cotangent principal symbol of a continuum differential
operator and its relation to the six-dimensional geometry compiler.

## 2. Dirac-type symbol theorem

Let `E` be a Hermitian bundle over an oriented real `n`-manifold and let `B`
be a first-order formally self-adjoint differential operator. Write

```text
b(xi)=sigma_1(B)(xi).
```

Assume the Dirac-type relation

```text
b(xi)b(eta)+b(eta)b(xi)=2 h(xi,eta) I_E,       (2.1)
```

where `h` is a positive contravariant quadratic form. Then

```text
sigma_2(B^2)(xi)=b(xi)^2=h(xi,xi) I_E.         (2.2)
```

For a positive action coefficient `kappa`, any Hessian whose leading part is

```text
L=kappa B^2 + terms of order at most one                 (2.3)
```

has scalar positive principal symbol

```text
sigma_2(L)(xi)=kappa h(xi,xi) I_E.             (2.4)
```

### Proof

Set `eta=xi` in (2.1). The left side is `2b(xi)^2`, which proves (2.2).
Principal symbols multiply under composition, while terms of order at most one
do not contribute to `sigma_2`. Multiplication by `kappa` gives (2.4). QED.

The metric is already encoded in the first-order symbol:

```text
h_ij I_E=(b(e_i)b(e_j)+b(e_j)b(e_i))/2.        (2.5)
```

Thus a selected full first-order operator is not compatible with an
independently adjustable metric table. Its Clifford anticommutator is that
table, up to the common normalization carried by the operator and action.

## 3. Dolbeault-HYM corollary

Let `(X,J,g)` be a Hermitian complex manifold and `E_A` a Hermitian bundle with
unitary connection `A`. On the Dolbeault complex define, in one conventional
normalization,

```text
B_A=sqrt(2)(dbar_A+dbar_A^*).
```

Its principal symbol is Clifford multiplication on `(0,*)` forms, so

```text
B_A^2=2 Delta_dbar,A
```

is of generalized Laplace type. Changing the `sqrt(2)` convention rescales
`h` and is absorbed into the single coefficient `kappa`; it does not create a
shape parameter.

The connection coefficients, curvature, HYM moment-map term, smooth Higgs
endomorphisms and Yukawa endomorphisms enter below second order. They can
change the potential, spectrum, kernel and Green operator, but not the scalar
quadratic principal symbol. Consequently:

> If the selected q79 upper differential is a genuine Dolbeault deformation
> operator on the selected Hermitian endpoint, then its self-adjoint closure
> charge automatically passes the CBF.T55 scalar-symbol gate.

This corollary does not select that endpoint or connection. In particular,
formal transport of an already-given hidden HYM complex does not instantiate
the visible-hidden physical operator.

## 4. Same-source composition with CBF.T55

Let the same selected geometry-action member emit:

1. the first-order symbol `b` of `B`;
2. the second-order Hessian `L=kappa B^2+lower order`;
3. the positive oriented Hilbert density coefficient `v`; and
4. one source hash binding these data to the same member.

Equation (2.5) recovers `h`. Equivalently, normalized trace of (2.4) and
polarization recover

```text
A=kappa h.
```

CBF.T55 then gives, in dimension `n`,

```text
c=(v^2 det A)^(1/n),
H=A/c,
G=c A^-1.                                      (4.1)
```

When the action normalization agrees with the Dirac normalization, `c=kappa`
and `H=h`. The metric and action scale are therefore emitted by the same
operator-density source; no second metric payload is permitted or required.

### Corollary 4.1 (reduced q79 exit contract)

For a q79 endpoint explicitly instantiated by a Dirac/Dolbeault source, the
following are not separate proof obligations:

```text
Dirac-type first-order symbol,
scalarity of the square,
metric coefficients,
Hodge coefficients.
```

The first item implies the second, equations (2.5) and (4.1) give the third,
and CBF.T52 gives the fourth. The endpoint must still emit the actual operator,
density, connection, domain, projector, reduced Green operator, symmetry
intertwiner and continuum error certificate.

## 5. Lower-order stability and the gauge-fixing boundary

Locally write

```text
B=b^i partial_i + b^i omega_i + Phi.
```

Only `b^i partial_i` contributes to `sigma_1(B)`. In `B^2`, the coefficient of
two derivatives is `b^i b^j`; connection, curvature and `Phi` terms contribute
at order one or zero. This proves lower-order stability without assuming a
flat HYM connection.

There is, however, a real boundary. A mixed-order gauge or detour complex need
not have a quadratic Laplace symbol. The existing q79 Costello certificate
explicitly excludes the naive mixed-order adjoint Hodge sum because its symbol
scales quartically. A corrected local gauge-fixed Hessian may be Laplace type,
but that is a separate operator construction. CBF.T56 therefore applies
directly to a genuine Dirac/Dolbeault complex and only after a valid gauge
fixing to a gauge-degenerate bosonic complex.

## 6. Exact non-diagonal six-dimensional witness

The executable certificate uses the non-diagonal determinant-one Hermitian
coframe from CBF.T52. Starting from the six standard `8 by 8` complex Clifford
matrices formed from Pauli tensor products, it pulls them through the exact
inverse-transpose coframe. The resulting matrices `gamma_i` satisfy all 21
independent relations

```text
gamma_i gamma_j+gamma_j gamma_i=2H_ij I_8,      (6.1)
```

where `H` is exactly the CBF.T52 contravariant metric.

For every polarization sample `e_i` and `e_i+e_j`, the certificate verifies

```text
(sum_i xi_i gamma_i)^2=(xi^T H xi) I_8.         (6.2)
```

Using the deliberately nonphysical action fixture `kappa=7` and density
`v=1`, the 21 second-order scalar samples reconstruct the same matrix
`A=7H` as CBF.T55. Formula (4.1) recovers `kappa=7`, the full non-diagonal
metric and the exact 64-dimensional Hodge digest from CBF.T52/T55.

A noncommuting order-zero potential is also inserted. It changes the linear
and constant coefficients of the high-frequency square but leaves every
quadratic coefficient equal to (6.2). This is an exact finite witness of the
order argument in Section 5.

## 7. Audit of existing q79 evidence

Three existing results are relevant but do not close the physical source:

1. The q79 Costello certificate proves a common scalar Laplace symbol for
   corrected gauge-fixed gauge, ghost, Higgs and squared-Weyl blocks on an
   auxiliary four-dimensional Euclidean compact-support regulator tier. It is
   not the six-dimensional q79 HYM endpoint.
2. The hidden shared-line HYM packet proves exact transport of the hidden
   Dolbeault Laplacian, harmonic kernel and reduced Green operator under a flat
   shared-line tensoring. It explicitly does not select a numerical HYM
   connection, visible/common endpoint or full rank-102 operator.
3. The q79 Hodge-action theorem proves the structural conditional formula
   `B_Q=dbar_Q+dbar_Q^*`, `Delta_Q=B_Q^2`. It explicitly leaves the physical
   endpoint, metric, connection and executed rank-102 operator open.

Their repository heads, paths and SHA-256 digests are recorded in the portable
evidence audit. They corroborate the operator class and its boundaries; they
are not premises of the exact Clifford theorem and are not promoted to current
physical authority here.

## 8. Frontier change

Before CBF.T56, the q79 source contract separately requested a scalar positive
Hessian symbol before T55 could run. After CBF.T56, a selected first-order
Dirac/Dolbeault operator plus its same-source density is sufficient:

```text
selected B_Q and Hilbert density
  -> scalar sigma_2(kappa B_Q^2) by theorem
  -> metric/action scale by T55
  -> Hodge response by T52.
```

This is a genuine reduction of proof obligations, not acceptance of a packet.
The missing physical object is now sharper:

```text
one hash-addressed selected q79 visible-hidden Hilbert complex carrying
dbar_Q, dbar_Q^*, density, HYM connection, domain, projector, reduced Green,
C4/TT naturality and certified finite/continuum errors.
```

`B.GEO.01` and `B.ACTION.01` remain open. Physical acceptance remains `0/3`
gates, `0/3` packets and `0/7` endpoint rows.

## 9. Parameter accounting

The theorem adds zero observed values, fitted values, continuous physical
parameters and discrete selectors. The benchmark `kappa=7` is a test fixture,
not a physical value. CBF.T56 removes one duplicated operator-class obligation;
it does not select the remaining common action primitive or absolute scale.

## 10. Reproduction

```powershell
python build_dirac_dolbeault_principal_symbol_bridge.py
python verify_dirac_dolbeault_principal_symbol_bridge.py
python -m unittest tests.test_dirac_dolbeault_principal_symbol_bridge -v
```
