# Q79 Fourier-Mukai Double-Qutrit Koszul and Augmented-Exterior Bridge Theorem v1

**Claim:** `CBF.T60`
**Date:** 2026-09-01
**Status:** `CLOSED EXACT SELECTED FIBER-COEFFICIENT AND AUGMENTED-EXTERIOR BRIDGE; PHYSICAL CONTINUUM INTERTWINER OPEN`

## 1. Result and boundary

The selected q79 construction contains two qutrits with different jobs.

1. A degree-three theta line on the marked elliptic curve has a
   three-dimensional section space. Relative Fourier-Mukai base change turns
   this theta space into the fiber of each selected rank-three transformed
   factor.
2. The three transformed factors carry the separate internal projective
   qutrit action already constructed by `UST.G3T`.

On a marked Fourier-Mukai chart the hidden fiber is therefore

```text
W9_y = H_theta,y tensor Q3_internal,
dim H_theta,y = dim Q3_internal = 3.                 (1.1)
```

Consequently its exact coefficient algebra is

```text
A2 = End(H_theta,y) tensor End(Q3_internal)
   = M3(C) tensor M3(C) = M9(C),
dim A2 = 81,             dim sl(A2) = 80.            (1.2)
```

This explains the hidden `81=1+80` before any continuum Galerkin choice. It
also distinguishes the two actions: the first is the finite theta datum in
the semihomogeneous Fourier-Mukai factor; the second is the internal action
over the identity on the three-factor orbit. They must not be called the same
translation.

The four commuting adjoint automorphisms generate an exact four-direction
Koszul-Hodge complex. Its harmonic dimensions are

```text
1, 4, 6, 4, 1.                                      (1.3)
```

The same sequence in `CBF.T58` is not merely a numerical match. The range of
its augmented projector is canonically an exterior power of a four-dimensional
symbol space. This theorem gives the exact exterior isomorphism.

What remains open is equally precise. A physical promotion needs a selected,
connection-compatible isometry from the four finite qutrit one-forms to that
four-dimensional augmented symbol space at the q79 endpoint. No such map is
inferred from equal ranks. The physical continuum Hessian, Green operator and
Galerkin projector remain open.

## 2. Why the coefficient algebra is selected

Let

```text
E = the marked eta9/Fermat elliptic curve,
L = O_E(3[0]).
```

Since `deg L=3>0`, Riemann-Roch and Serre duality give

```text
h0(E,L tensor P_y)=3,       h1(E,L tensor P_y)=0       (2.1)
```

for every degree-zero Poincare line `P_y`. Cohomology and base change therefore
make the relative transform locally free of rank three, with fiber

```text
H_theta,y = H0(E,L tensor P_y).                       (2.2)
```

The level-three theta group acts projectively on (2.2). In the orientation
fixed by the eta9 theta series its generators obey

```text
X^3=Z^3=I,             XZ=omega ZX,
omega^2+omega+1=0.                                  (2.3)
```

The three-factor orbit supplies a second copy `Q3_internal`. Equation (1.2)
is therefore a fiber-coefficient identity produced by the selected transform,
not a discretization assumption. Projective scalar cocycles disappear on
endomorphisms, so each copy has an honest adjoint action.

The tensor display is chartwise. Globally, the Fourier-Mukai factor is a
projective homogeneous object and the internal action is a projective action
over the identity. Their endomorphism and adjoint bundles are honest, but a
strict global splitting of the full elliptic translation extension is not
claimed.

## 3. Four commuting finite directions

Write `A=M3(Q(omega))` and `A2=A tensor A`. Define

```text
alpha_v = Ad_X tensor id,       beta_v = Ad_Z tensor id,
alpha_i = id tensor Ad_X,       beta_i = id tensor Ad_Z. (3.1)
```

All four automorphisms commute. Within each factor the central phase in
`XZ=omega ZX` cancels under conjugation; across factors commutation is
literal.

Let `theta_0,...,theta_3` be exterior generators and put

```text
C^k=A2 tensor Lambda^k(C^4),
d(a)=sum_j (gamma_j(a)-a) theta_j,                    (3.2)
```

extended by the Koszul sign rule. Here
`gamma=(alpha_v,beta_v,alpha_i,beta_i)`. Commutativity gives `d^2=0`.

On the Weyl basis

```text
W_ab tensor W_cd = Z^a X^b tensor Z^c X^d             (3.3)
```

the four difference coefficients are

```text
p = (omega^a-1, omega^(-b)-1,
     omega^c-1, omega^(-d)-1).                        (3.4)
```

Indeed `Ad_X(Z^a X^b)=omega^a Z^a X^b` and
`Ad_Z(Z^a X^b)=omega^(-b) Z^a X^b`. Thus the negative exponents belong to
the two `Ad_Z` directions; they are not additional sign choices.

With the Frobenius metric on `A2` and the standard exterior metric, the Hodge
Laplacian on every exterior component of a mode is scalar:

```text
Delta(a,b,c,d)=3 N(a,b,c,d),                          (3.5)
```

where `N` is the number of nonzero entries among `a,b,c,d` modulo three.
The exact degree-zero spectrum is the coefficient list of `(1+2t)^4`:

```text
eigenvalue       0    3    6    9    12
multiplicity     1    8   24   32    16.              (3.6)
```

The kernel is the scalar center. The reduced Green eigenvalues are
`1/3,1/6,1/9,1/12`. Restricting the coefficient lane to `sl9` removes the
center, so its exact finite Hodge gap is `3`.

Every nonzero mode Koszul complex is contractible. The zero mode has zero
differential, hence

```text
H^k(C,d)=C I9 tensor Lambda^k(C^4),
dim H^k=(1,4,6,4,1).                                  (3.7)
```

This is the two-qutrit extension of the one-qutrit complex in `CBF.T04`.
Tensoring the latter with the identity in either factor recovers either
two-direction face of (3.2).

## 4. Centered logarithms are a finite compiler

Each adjoint generator is unitary, has order three and has no eigenvalue
`-1`. Its principal centered logarithm is therefore unique. On a Weyl label
`r in {0,1,2}`, let

```text
bar(r)=0,1,-1,
ell_X(r)=bar(r),        ell_Z(r)=-bar(r).              (4.1)
```

The logarithm eigenvalue is `(2 pi i/3) ell`. Exponentiation returns the
finite adjoint generator exactly.

For one direction set

```text
R(ell)=(exp(2 pi i ell/3)-1)/(2 pi i ell/3),
R(0)=1.                                                (4.2)
```

On an exterior basis subset `S`, multiply by `prod_(j in S) R(ell_j)`.
These diagonal maps give a chain isomorphism from the centered-log Koszul
complex to the finite-difference Koszul complex, because

```text
(exp lambda_j-1) prod_(i in S)R(lambda_i)
 =lambda_j prod_(i in S union {j})R(lambda_i).         (4.3)
```

For every nonzero qutrit exponent,

```text
|R| = 3 sqrt(3)/(2 pi),       |R|^2=27/(4 pi^2).       (4.4)
```

Thus the centered log is a canonical finite-coordinate compiler with an exact
condition number. It is not yet a continuum derivative.

## 5. Exact augmented-exterior bridge

At a nonzero cotangent vector, `CBF.T58` has

```text
Ran P_n = (C alpha tensor Lambda^n C^3)
          direct-sum Lambda^(n+1) C^3,
n=-1,0,1,2,3.                                         (5.1)
```

Let `V4=C e0 direct-sum V3`, with `V3=C^3`, and identify `e0` with the
normalized `alpha` line. Exterior decomposition gives the explicit isometry

```text
J_n: Lambda^(n+1)V4 -> Ran P_n,
J_n(e0 wedge eta + zeta)=alpha tensor eta direct-sum zeta. (5.2)
```

Therefore

```text
rank Ran P_n=C(3,n)+C(3,n+1)=C(4,n+1),                (5.3)
```

and (1.3) follows as an identity of exterior constructions.

Equation (5.2) closes the abstract carrier bridge. A physical bridge still
requires a selected map

```text
I_(x,xi): span(theta_vX,theta_vZ,theta_iX,theta_iZ)
          -> C alpha_(x,xi) direct-sum T^(0,1)*_x X    (5.4)
```

that preserves the metric, orientation, connection, domains and the endpoint
residual. An arbitrary `U(4)` choice in (5.4) is not accepted. Equal ranks do
not select it.

## 6. Why this is not a scalar Fourier cutoff

The marked Fermat elliptic curve is equianharmonic. Up to an overall positive
scale, its dual lattice quadratic form is

```text
Q(u,v)=2u^2+2uv+2v^2.                                 (6.1)
```

For the adjoint character `(a,b)`, scalar Fourier lifts have residue

```text
(u,v)=(bar(a),-bar(b)) mod 3.                          (6.2)
```

Minimizing (6.1) in all nine residue classes gives:

```text
minimum Q       0       2       6
number of modes 1       6       6.                    (6.3)
```

The last six modes come from two character sectors with three minimizing
lattice representatives each. The full spectral subspace below the next
level has rank `13`, not `9`; its next eigenvalue is `8`, so the `6` to `8`
gap is strict. Selecting one vector from each triply degenerate sector would
require extra data.

This is an exact no-go for identifying the selected `M3` coefficient algebra
with the lowest scalar-Fourier band. The coefficient algebra is exact because
it is `End H0(E,L tensor P_y)`, while continuum modes remain sections valued
in that algebra. This distinction eliminates a hidden cutoff assumption.

## 7. Frontier change

Closed here:

- the selected local Fourier-Mukai theta-fiber source of the first `M3`;
- the separation and tensor composition of vertical-theta and internal
  qutrit coefficient factors;
- the exact `81=1+80` hidden coefficient algebra;
- the four-generator finite Koszul differential, Hodge spectrum, Green
  operator and cohomology;
- the centered-log to finite-difference chain isomorphism;
- the canonical exterior-space explanation of T58's `1,4,6,4,1` pattern;
- the equianharmonic rank-13 scalar-Fourier no-go.

Still open:

- the selected global map (5.4) and its connection/domain covariance;
- the same-source visible/common Hull-Strominger endpoint;
- the physical augmented Hessian coefficients, harmonic projector and
  reduced Green operator;
- controlled continuum-to-finite comparison beyond the exact coefficient
  typing proved here.

Accordingly `B.GEO.01` and `B.OP.01` remain open. Physical counters do not
move. The advance is a new exact source and typing theorem, not a physical
endpoint claim.

## 8. Parameters and reproducibility

No observed value, fitted coefficient, continuous physical parameter or new
discrete selector is used. The overall elliptic metric scale cancels from the
rank-13 cutset.

Run:

```powershell
python build_q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.py
python verify_q79_fourier_mukai_double_qutrit_augmented_exterior_bridge.py
python -m unittest tests.test_q79_fourier_mukai_double_qutrit_augmented_exterior_bridge -v
```

Primary mathematical inputs include Atiyah's classification of elliptic-curve
bundles, Mukai's Fourier-Mukai and semihomogeneous-bundle results, and Brion's
classification of homogeneous projective bundles:

- M. F. Atiyah, *Vector Bundles over an Elliptic Curve*, Proc. London Math.
  Soc. 7 (1957), https://doi.org/10.1112/plms/s3-7.1.414.
- S. Mukai, *Semi-homogeneous Vector Bundles on an Abelian Variety*, J. Math.
  Kyoto Univ. 18 (1978), https://doi.org/10.1215/KJM/1250522574.
- S. Mukai, *Duality Between D(X) and D(X-hat) with Its Application to
  Picard Sheaves*, Nagoya Math. J. 81 (1981),
  https://doi.org/10.1017/S002776300001922X.
- M. Brion, *Homogeneous Projective Bundles over Abelian Varieties*, Algebra
  Number Theory 7 (2013), https://doi.org/10.2140/ant.2013.7.2475.
