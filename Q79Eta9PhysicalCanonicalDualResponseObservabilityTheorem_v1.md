# CBF.T73 q79 eta9 physical canonical-dual response observability theorem

## Status

`CLOSED_EXACT_PHYSICAL_MIDPOINT_CANONICAL_DUAL_RESPONSE_PROJECTIVE_RANK122`

CBF.T72 proves that three physical coefficient-evaluation quotients separate
the full rank-122 projective graph tangent. H4-T145 independently constructs
an invertible canonical-dual bilinear on the holomorphic differential space of
each selected midpoint curve. T73 proves that these are not unrelated
82-dimensional spaces: K3 adjunction canonically identifies every T72 quotient
with the corresponding H4 holomorphic differential space. It then computes
the exact rank of the composed local response.

## 1. The coefficient quotient

Let `S` be the selected degree-two K3 surface, with primitive polarization
`H`, `H^2=2`, and let

```text
L=O_S(9H),                 dim H0(S,L)=83.
```

At a physical elliptic-base point `e`, evaluation of the selected eta9 member
gives a section `F_e` of `L` and a curve

```text
C_e=(F_e=0) in S.
```

The output of the T72 row is exactly

```text
Q_e=H0(S,L)/<F_e>,         dim Q_e=82.
```

For `edge-0`, `edge-1`, and `edge-2`, the quotient pivots used by T72 are
respectively `5,5,11`. They agree exactly with the dynamic fiber charts in
H4-T134. T134 is used here only to audit coordinate identity. Its binary64
fiber-to-Gauss-Manin residual is not used as an exact premise.

## 2. The adjunction bridge

The selected midpoint curves are smooth genus-82 curves. Since `K_S` is
trivial, adjunction gives

```text
K_Ce = O_Ce(C_e).
```

The divisor sequence is therefore

```text
0 -> O_S --F_e--> O_S(9H) -> K_Ce -> 0.                 (1)
```

A K3 surface has `H0(S,O_S)=C` and `H1(S,O_S)=0`. Taking global sections of
(1) consequently gives the exact sequence

```text
0 -> C F_e -> H0(S,O_S(9H)) -> H0(C_e,K_Ce) -> 0.       (2)
```

Thus restriction induces a canonical isomorphism

```text
A_e: Q_e -> H0(C_e,K_Ce).                               (3)
```

This is an actual map theorem, not a dimension-count identification. The
dimensions independently agree by K3 Riemann-Roch and adjunction:

```text
C_e^2 = (9H)^2 = 162,
g(C_e) = 1+C_e^2/2 = 82,
h0(S,O_S(9H)) = 2+C_e^2/2 = 83,
dim Q_e = 83-1 = 82.
```

## 3. The canonical-dual map

H4-T145 works in

```text
V_e=H0(C_e,K_Ce)=H^{1,0}(C_e)
```

and constructs the selected symmetric map

```text
B_e^flat=S_e theta_e: V_e -> V_e^*.
```

At the same three physical midpoints its Arb determinant balls have positive
lower bounds:

```text
edge-0   > 7e-498,
edge-1   > 6e-465,
edge-2   > 1e-528.
```

Hence every `B_e^flat` is an isomorphism. Combining it with (3) gives

```text
J_e=B_e^flat A_e: Q_e -> V_e^*.
```

The direct sum `J=J_0+J_1+J_2` is an isomorphism of rank `3*82=246`.

## 4. Exact response rank

Let

```text
R: T_graph^aff -> Q_0 + Q_1 + Q_2
```

be the three-row T72 coefficient-evaluation map. T72 proves

```text
dim T_graph^aff = 123,
rank R = 122,
ker R = the one-dimensional radial member line.
```

Define the local canonical-dual response

```text
D=J R=(direct sum_e B_e^flat A_e) R.                    (4)
```

Because `J` is invertible,

```text
ker D = ker R,
rank D = rank R = 122.
```

After quotienting the radial member line, (4) has projective kernel zero.
Therefore the three selected physical midpoint rows jointly observe every
projective graph-preserving tangent direction in canonical Hodge/Serre dual
coordinates.

## 5. Geometric carrier support

H4-T159 certifies all `198` normalization-ramification branches and all `54`
conductor-node branches over the complete T72 parameter boxes around
`edge-0` and `edge-1`. H4-T155 supplies the same `252`-branch conclusion on
the wider `edge-2` box. Thus every row in (4) is attached to a complete,
collision-free selected-source carrier, rather than to a formal evaluation
point lacking local geometric support.

This carrier statement is positive-width. The canonical bilinear
nondegeneracy used in (4) is presently certified at the three midpoint balls.
T73 does not silently extend that nondegeneracy to the whole `2^-32` product.

## 6. Intrinsic provenance

The post-map is not an arbitrary invertible matrix. H4-T146 derives its
intrinsic Cech/Serre form from the normalized ramification divisor,

```text
B_R(i,j)=sum_p g_i(p)g_j(p)G_t(p)/(G_x(p)^2 G_yy(p)),
```

and certifies the selected-origin evaluation on all 198 ramification points.
H4-T147 rewrites the same expression as a root-label-independent trace in the
degree-198 finite etale ramification algebra and derives its directed
derivative rule. Those results explain the geometric origin of `B`; T73 uses
H4-T145's midpoint nondegeneracy for its exact rank proof and does not pretend
that T146/T147 already supply a pathwide midpoint-panel evaluation.

## 7. The theorem

**Physical Canonical-Dual Response Observability Theorem.** For the exact
selected characteristic-zero q79 eta9 member, the T72 coefficient-evaluation
quotient at each of `edge-0@1/2`, `edge-1@1/2`, and `edge-2@1/2` is canonically
isomorphic, by K3 adjunction, to the holomorphic differential space used by
H4-T145. Postcomposition with the three certified nondegenerate canonical-dual
forms produces a rank-122 map on the rank-123 affine graph tangent whose
kernel is exactly the radial member line. The induced projective response is
injective.

**Proof.** Exactness of (2) proves that all three `A_e` are isomorphisms.
H4-T145 proves that all three `B_e^flat` are isomorphisms. Their direct sum `J`
is therefore invertible. For any linear map `R` and invertible post-map `J`,
`ker(JR)=ker(R)` and `rank(JR)=rank(R)`. Applying T72's exact rank and radial-
kernel certificate proves the statement. H4-T159 and H4-T155 supply the
matching local branch carriers. QED.

## 8. Frontier change and boundary

T73 closes the missing exact bridge

```text
physical coefficient quotient
  -> K3 adjunction
  -> holomorphic differential
  -> canonical Hodge/Serre dual response.
```

It does not prove that this local response is the divisor-to-Picard,
Abel-Jacobi, normal-function, or closed-loop BHT derivative. It also does not
execute rank-164 Gauss-Manin transport, the 248-row handle integral, integral
period reduction, `beta_C`, `U_eta9`, or a HYM/SM/QG endpoint.

The next non-repetitive calculation is to evaluate the H4-T147 finite-trace
bilinear over the T159/T155 parameter boxes and certify that the three
`B_e^flat(s)` remain invertible there. That would upgrade T73 from three
midpoint response maps to a quantitative positive-width response theorem and
prepare the rows for global transport.

## 9. Reproduction

```powershell
python build_q79_eta9_physical_canonical_dual_response_observability.py
python verify_q79_eta9_physical_canonical_dual_response_observability.py
python -m unittest tests.test_q79_eta9_physical_canonical_dual_response_observability -q
```

The packet SHA-256 is

```text
5e7a4d37026be0154511d60cadb48a6e93a927d8c24309b2b970110910f4cd8a
```

No observed quantity, fitted parameter, or new discrete selector enters the
construction.
