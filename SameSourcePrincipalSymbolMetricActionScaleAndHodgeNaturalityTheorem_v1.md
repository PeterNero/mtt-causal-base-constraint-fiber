# Same-Source Principal-Symbol Metric, Action-Scale and Hodge-Naturality Theorem

**Identifier:** CBF.T55  
**Date:** 2026-09-01  
**Tier:** exact general theorem plus exact source-locked benchmark  
**Physical status:** conditional source reduction. This theorem does not supply
the selected q79 Hessian, density, HYM connection, Green operator or physical
endpoint.

## 1. Purpose

CBF.T52 proves that a supplied positive Hermitian metric determines the full
six-dimensional Hodge operator and its first response in all eight
fixed-volume Hermitian shape directions. Its physical boundary correctly
leaves those metric coefficients open.

The seven-row endpoint theorem, however, already requires one geometry-action
packet `GAS`. Supplying a metric table independently of the principal symbol
of the same action Hessian would duplicate data if that symbol is scalar and
Laplace type. The question here is therefore:

```text
same-source action Hessian principal symbol + same-source density
  -> action scale + metric
  -> T52 Hodge operator and first response.
```

The answer is yes under an explicit, checkable scalar-symbol hypothesis. The
result is a source-contract theorem, not a construction of the missing
physical source.

## 2. Typed input

Let `V` be an oriented real vector space of dimension `n`, let `E` be a
Hermitian vector space of rank `r`, and let `L` be a second-order operator on
`E`-valued fields. Its principal symbol is a quadratic map

```text
S(xi)=sigma_2(L)(xi) in End(E).
```

The required same-source inputs are:

1. the complete principal symbol `S`;
2. a positive density coefficient `v` in the same oriented coframe;
3. a source hash identifying both as outputs of one `GAS` member;
4. when Hermitian geometry is claimed, the supplied complex structure `J`.

The scalar Laplace-type gate is

```text
S(xi)=a(xi) I_E,
a(xi)=(1/r) Tr_E S(xi),                         (2.1)
```

with `a` positive definite. This gate must be verified; taking only the trace
of a nonscalar symbol is insufficient.

## 3. Metric and action-scale reconstruction

Polarize `a` to obtain the positive contravariant matrix `A`:

```text
A_ii=a(e_i),
A_ij=(a(e_i+e_j)-a(e_i)-a(e_j))/2.              (3.1)
```

For a Laplace-type action Hessian there are a positive action coefficient `c`
and a covariant metric `G` such that

```text
A=c H,
H=G^-1,
v=sqrt(det G).                                  (3.2)
```

### Theorem 3.1 (same-source reconstruction)

Given (2.1), positive `A` and positive `v`, equations (3.2) have exactly one
positive solution:

```text
c=(v^2 det A)^(1/n),
H=A/c,
G=c A^-1.                                       (3.3)
```

If `a(J^*xi)=a(xi)`, the reconstructed `G` is Hermitian for `J`.

### Proof

Taking determinants in `A=cG^-1` gives

```text
det A=c^n/det G=c^n/v^2.
```

Positivity selects the unique positive `n`th root in (3.3). Substitution then
gives `H` and `G`, and any second positive solution must have the same `c`,
then the same `H` and `G`. Invariance of the quadratic form under `J^*` is
equivalent to `J^T G J=G`. QED.

### Corollary 3.2 (no duplicate metric payload)

Once one accepted `GAS` packet supplies a scalar positive principal symbol and
its density, the metric coefficients are not an additional source packet.
They are coefficients of the same symbol. The eight fixed-volume Hermitian
shape functions remain genuine local geometric degrees of freedom, but they
are not eight extra fit parameters or eight independently supplied endpoint
rows.

## 4. The scale boundary

The density is essential. If only `A` is supplied, then for every `lambda>0`

```text
c' = lambda c,
G' = lambda G                                  (4.1)
```

gives the same `A=cG^-1`. Its density changes by
`lambda^(n/2)`. Thus the symbol alone determines the conformal metric only up
to one positive joint action/metric-scale orbit. This is the same type of
normalization boundary already isolated by CBF.T49-T50; it is not a new set of
shape parameters.

Scalarity is independently essential. A nonscalar endomorphism-valued symbol
can have the same normalized trace as a scalar one while acting differently on
fiber polarizations. In that case (3.1) recovers only a traced quadratic form,
not a common Laplace-type metric for the full operator.

## 5. Hodge composition

For `n=6`, apply CBF.T52 to the reconstructed `G`. With `H=G^-1`, the complete
Hodge matrix is

```text
star_G(e_J)
 = sum_(|I|=|J|)
   epsilon(I,I^c) v det(H[I,J]) e_(I^c).        (5.1)
```

### Theorem 5.1 (symbol-to-Hodge determinacy)

Under the hypotheses of Theorem 3.1, the complete Hodge operator is a
deterministic algebraic function of `(S,v)`. No metric coefficients can be
changed while preserving both the full scalar symbol and density.

### Proof

Theorem 3.1 uniquely reconstructs `G` and `H`; equation (5.1) then uniquely
constructs every Hodge coefficient. QED.

This is stronger than matching spectra or traces. It uses the full quadratic
principal symbol and therefore retains directional information.

## 6. First variation

Let the same source vary through `(S(t),v(t))`. Polarization gives `A(t)`. Put

```text
gamma=dot(c)/c
     =(1/n)[2 dot(v)/v + Tr(A^-1 dot(A))].       (6.1)
```

Differentiating (3.3) gives

```text
dot(H)=dot(A)/c-gamma H,
dot(G)=gamma G-G[dot(A)/c]G.                    (6.2)
```

CBF.T52 then gives on `k`-forms

```text
dot(star_G)
 =star_G[(1/2)Tr(G^-1 dot(G))Id
          -Lambda^k((G^-1 dot(G))^T)].          (6.3)
```

### Theorem 6.1 (closure of the response chain)

Equations (3.1), (6.1), (6.2) and (6.3) give the unique first Hodge response
from the first symbol and density response. On the volume-one Hermitian shape
tangent, this composite has rank eight.

### Proof

Equations (6.1) and (6.2) are derivatives of the unique reconstruction. For a
fixed-volume shape variation with fixed action scale, `dot(v)=gamma=0`, so
`dot(A)=c dot(H)=-cH dot(G)H`. Substitution in (6.2) recovers `dot(G)` exactly.
CBF.T52 proves that `dot(G) -> dot(star_G)` is injective on the eight-dimensional
Hermitian shape tangent. The composite therefore has rank eight. QED.

## 7. Gauge and base naturality

Internal unitary conjugation sends

```text
S(xi) -> U S(xi) U^-1.
```

It preserves normalized trace and preserves the scalar-symbol gate. Hence it
does not change `A`, `c`, `G` or `star_G`.

Let `F` be an orientation-preserving base isomorphism. Pulling back the symbol
and density gives the usual transformed quadratic form and volume. The
reconstruction obeys

```text
G(F^*S,F^*v)=F^*G(S,v),
F^* star_G = star_(F^*G) F^*.                   (7.1)
```

### Theorem 7.1 (same-source naturality)

The reconstruction and Hodge composition are natural under internal unitary
gauge changes and orientation-preserving base changes. Therefore a physical
`GAS -> SYN` map need only certify the principal-symbol and density
intertwining; a second independent table of transformed Hodge coefficients is
not required.

### Proof

Trace is conjugation invariant. Polarization is functorial under linear
pullback, determinants transform with the density Jacobian, and inversion is
natural. Equation (7.1) is then the defining naturality of the Hodge operator.
The packet verifies the complete `64 by 64` identity for a nonorthogonal
determinant-one complex-linear coframe change. QED.

## 8. Exact benchmark

The executable certificate consumes the exact non-diagonal determinant-one
Hermitian metric from CBF.T52. It chooses internal rank four and `c=7`, forms

```text
A=7G^-1,
S(xi)=(xi^T A xi) I_4,                           (8.1)
```

and emits the 21 samples at `e_i` and `e_i+e_j`. From only those samples and
`v=1`, it reconstructs

```text
det A=7^6=117649,
c=7,
H=A/7,
G=7A^-1.                                        (8.2)
```

The reconstructed full Hodge matrix has exactly the CBF.T52 digest. A
nonorthogonal complex-linear determinant-one coframe shear satisfies the full
exterior naturality identity. The eight T52 shape directions are pushed
through the symbol variation formulas and recover the same eight Hodge
derivative digests with rank eight.

Two exact negative controls are included:

1. deleting `v` leaves the one-positive-scale orbit (4.1);
2. replacing one scalar symbol sample by a nonscalar diagonal endomorphism
   preserves its trace but fails the scalarity residual test.

## 9. Frontier change

The source contract is now:

```text
accepted same-root GAS
  supplies scalar positive sigma_2(Hess A) and density
    -> unique action scale and six-metric
    -> unique full T52 Hodge response
    -> SYN may consume these by naturality.
```

This closes the duplicate metric-row question. It does not accept a physical
packet. The following remain open:

```text
selected q79 visible-hidden HYM member and beta_C root,
physical scalar Laplace-type upper Hessian and its source hash,
Fu-Yau conformal factor and positive density on that member,
connection, domains, projector and reduced Green operator,
C4/monodromy or direct TT naturality on the physical complex,
rank-102 execution and certified finite/continuum errors,
Lorentzian/BV action, QME pushforward and observables.
```

Accordingly `B.GEO.01` and `B.ACTION.01` remain open, physical packet
acceptance remains `0/3`, and physical endpoint-row acceptance remains `0/7`.
The exact advance is that an accepted scalar-symbol `GAS` packet will not need
an additional eight-coordinate metric payload before the Hodge compiler can
run.

## 10. Parameter accounting

No observed values, fitted values, continuous parameters or discrete selectors
enter the theorem. The benchmark value `c=7` is an exact test fixture, not a
physical value. The one shared action primitive remains unresolved at the
physical tier. The theorem removes duplicated source bookkeeping; it does not
reduce the intrinsic local dimension of Hermitian metric space.

## 11. Reproduction

```powershell
python build_same_source_principal_symbol_metric_hodge_naturality.py
python verify_same_source_principal_symbol_metric_hodge_naturality.py
python -m unittest tests.test_same_source_principal_symbol_metric_hodge_naturality -v
```

