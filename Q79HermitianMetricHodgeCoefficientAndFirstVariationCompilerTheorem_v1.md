# q79 Hermitian-Metric Hodge-Coefficient and First-Variation Compiler Theorem

**Identifier:** CBF.T52
**Date:** 2026-08-31
**Tier:** exact supplied-metric compiler
**Physical status:** this theorem does not select the physical q79 metric,
Fu-Yau conformal factor, common visible-hidden HYM connection, gauge
projectors, rank-102 differential, chirality, action or quantum pushforward.

## 1. Purpose and boundary

CBF.T51 supplies the complete Hodge sign table after an oriented orthonormal
coframe has been supplied. It also proves that orientation and unit volume do
not determine the eight fixed-volume Hermitian shape directions. The open
question addressed here is narrower and exact:

```text
supplied positive Hermitian metric
  -> all 64 by 64 Hodge coefficients
  -> first response in all eight shape directions.
```

This is the missing coefficient compiler between an eventual selected q79
metric and the T51 sign table. It is not a source theorem for that metric.
In particular, it does not solve the same-member `beta_C` root `EA.03R`, the
Fu-Yau/Strominger system, or `B.HS.01` and `B.GEO.01`.

## 2. Exterior conventions

Let `V` be an oriented real vector space of dimension `n=6` with coordinate
coframe `e1,...,e6` and orientation

```text
nu=e1 wedge ... wedge e6.
```

For an ordered subset `I`, write `e_I` for the corresponding exterior basis
form and `I^c` for its ordered complement. Let `epsilon(I,I^c)` be the sign
of the permutation formed by listing `I` followed by `I^c`.

Supply a positive covariant metric matrix `G`, its inverse `H=G^-1`, and the
positive volume factor

```text
v=sqrt(det G).
```

For equal-cardinality subsets `I,J`, let `H[I,J]` be the indicated minor.
The induced covector metric is

```text
<e_I,e_J>_G=det H[I,J].                          (2.1)
```

## 3. Exact metric-to-Hodge coefficient formula

### Theorem 3.1

For every exterior basis form `e_J`, the Hodge operator is

```text
star_G(e_J)
 = sum_(|I|=|J|)
   epsilon(I,I^c) v det(H[I,J]) e_(I^c).         (3.1)
```

Equivalently, the coefficient of `e_(I^c)` in `star_G(e_J)` is

```text
epsilon(I,I^c) v det(H[I,J]).                    (3.2)
```

It is the unique linear operator satisfying

```text
e_I wedge star_G(e_J)=det(H[I,J]) v nu.          (3.3)
```

### Proof

Only the `e_(I^c)` term can contribute to the coefficient of `nu` in the
wedge product with `e_I`. Its wedge sign is `epsilon(I,I^c)`. Multiplying
that sign by the coefficient (3.2) gives the right side of (3.3), because
the sign squares to one. Equation (2.1) identifies the right side with the
defining Hodge pairing. Since the exterior basis spans each degree, the
defining identity also proves uniqueness. QED.

### Corollary 3.2

The finite formula obeys

```text
star_G^2=(-1)^(k(6-k)) Id                         (3.4)
```

on degree `k`, and it is an isometry between degree `k` and degree `6-k`.

### Proof

These are the standard algebraic consequences of the defining identity for
the Hodge operator on an oriented positive inner-product space. They can also
be checked directly from the complementary minors of `H` and Jacobi's minor
identity. The certificate performs the direct matrix checks on all 64 basis
states and all 924 equal-degree ordered basis pairs. QED.

When `G=I6` and `v=1`, the minor in (3.2) is `delta_(I,J)`. Thus (3.1)
specializes exactly, coefficient for coefficient, to the T51 signed
permutation table. The degree-zero and degree-six rows remain

```text
star_G(1)=v nu,
star_G(nu)=v det(H)=v^-1.                        (3.5)
```

For `det G=1`, both normalized orientation rows equal one.

## 4. Exact first variation

Let `G(t)` be a differentiable family of positive metrics and put

```text
dotG=(d/dt)G(t)|_0,
A=G^-1 dotG.
```

Let `A_[k]^*` denote the derivation induced by `A^T` on covariant `k`-forms:

```text
A_[k]^*(xi1 wedge ... wedge xik)
 = sum_r xi1 wedge ... wedge (A^T xir) wedge ... wedge xik.   (4.1)
```

### Theorem 4.1 (Hodge first-variation formula)

On degree `k`,

```text
dot(star_G)
 = star_G [ (1/2) tr(A) Id - A_[k]^* ].          (4.2)
```

### Proof

Differentiate the two metric quantities in (3.1):

```text
dotH=-H dotG H,
dotv=(1/2)tr(H dotG)v.                           (4.3)
```

The derivative of a determinant is the sum obtained by replacing one row
or one column by its derivative. Applying that rule to every minor
`det(H[I,J])` in (3.1), the volume derivative gives the first term of (4.2),
while the differentiated inverse-metric slots give the exterior derivation
`-A_[k]^*`. This proves (4.2). The executable proof computes the derivative
of every minor independently and compares it entrywise with (4.2), both at
the identity and at a non-diagonal Hermitian metric. QED.

Equation (4.2) is finite and exact. Rational metrics of square determinant
with exact `v` are evaluated over rational arithmetic. More general exact
algebraic or interval data can use the same finite minors with their supplied
exact or interval volume root; no spectral truncation is introduced here.

## 5. The eight Hermitian shape directions

Fix the standard complex structure with real pairs

```text
(e1,e2), (e3,e4), (e5,e6).
```

The real tangent space to positive Hermitian `3 by 3` matrices is
`Herm(3)`, of real dimension nine. Fixing volume imposes
`tr(G^-1 dotG)=0`, leaving the eight-dimensional traceless Hermitian space.
A real basis consists of

```text
2 traceless diagonal directions,
3 real off-diagonal directions,
3 imaginary off-diagonal directions.            (5.1)
```

### Theorem 5.1 (rank-eight shape response)

The derivative map

```text
dotG -> dot(star_G)                               (5.2)
```

is injective on the fixed-volume Hermitian shape tangent. Consequently the
full Hodge operator detects all eight shape directions.

### Proof

It is enough to restrict (4.2) to one-forms. Fixed volume gives `tr(A)=0`, so

```text
dot(star_G)|_(Lambda^1)=-star_G A^T.              (5.3)
```

The Hodge operator is invertible. If the left side vanishes, then `A^T=0`,
so `A=0`, hence `dotG=GA=0`. Thus (5.2) is injective on every subspace of
fixed-volume variations, including the eight-dimensional Hermitian shape
space. QED.

The exact packet emits the basis (5.1), verifies symmetry, complex-structure
compatibility and zero relative trace, and obtains rank eight from the
flattened `64 by 64` derivative matrices at two metrics.

## 6. Non-diagonal exact witness

To ensure the implementation is not only a diagonal rescaling, use the
complex coframe matrix

```text
      [1  1+i   0 ]
M  =  [0   1   1-i]
      [0   0    1 ].                             (6.1)
```

Its complex determinant is one. Let `R(M)` be its real `6 by 6`
realification in the fixed complex pairs and define

```text
G=R(M)^T R(M).                                   (6.2)
```

Then `G` is symmetric, positive, non-diagonal, Hermitian for the standard
complex structure and has determinant one. The packet emits `G`, `G^-1`, all
leading principal minors, the complete sparse Hodge matrix, and all eight
first derivatives. It verifies:

```text
G G^-1=I6,
J^T G J=G,
star_G^2=(-1)^(k(6-k)),
e_I wedge star_G(e_J)=det(G^-1[I,J])nu,
rank{dot(star)_1,...,dot(star)_8}=8.              (6.3)
```

The witness is a unit test for the universal formula. It is not proposed as
the selected q79 Fu-Yau metric.

## 7. q79 and proto-spinor status after T52

The exact separation is now:

```text
oriented orthonormal Hodge sign table                 closed by T51,
supplied metric -> all Hodge coefficients             closed by T52,
eight Hermitian shape -> first Hodge response          closed by T52,
selected q79 metric endomorphism coefficients          open,
selected Fu-Yau conformal factor                       open,
same-member beta_C root EA.03R                         open,
common visible-hidden HYM metric and connection        open,
gauge projector values                                 open,
rank-102 Dbar, domains, projector and Green             open,
physical C4/direct TT intertwiner                       open,
associated chiral operator and index                   open,
upper action and QME transport                         open.
```

For the proto-spinor dependency table, the metric-endomorphism coefficient
compiler can therefore be marked closed, while its selected coefficients,
HYM correction coefficients and gauge projector values remain open.

This result also does not bypass the graph-Prym endpoint. The existing exact
promotion interface has a 122-dimensional projective tangent and a
126-dimensional normal response; it has not emitted an accepted same-member
zero of the 248-component `beta_C` row. A physical q79 metric still has to be
emitted by that selected geometry or by another independently accepted
source theorem.

## 8. Parameter and physical ledger

T52 uses no measured values, fitted values or empirical replay. It adds

```text
continuous physical parameters: 0,
discrete selectors:              0,
shared action primitives:        1 -> 1.
```

The eight shape components are unresolved local source fields, not eight free
fit parameters. Calling them parameters would conceal the remaining source
problem; assigning witness values to them would be a benchmark, not closure.

Accordingly the controlling blockers remain open:

```text
B.HS.01, B.GEO.01, B.ACTION.01, B.QFT.02.
```

Physical acceptance remains exactly

```text
0/3 gates,
0/3 packets,
0/7 rows.
```

## 9. Reproduction

The machine-readable contract and source lock are

```text
q79_hermitian_metric_hodge_compiler_contract.schema.json
q79_hermitian_metric_hodge_compiler_source_lock.json
```

Build and independently verify with

```text
python build_q79_hermitian_metric_hodge_compiler.py
python verify_q79_hermitian_metric_hodge_compiler.py
python -m unittest tests.test_q79_hermitian_metric_hodge_compiler -v
```

The generated artifact is

```text
q79_hermitian_metric_hodge_compiler.packet.json.
```
