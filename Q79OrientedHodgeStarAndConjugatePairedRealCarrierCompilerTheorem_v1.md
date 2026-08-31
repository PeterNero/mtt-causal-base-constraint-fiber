# q79 Oriented Hodge-Star and Conjugate-Paired Real-Carrier Compiler Theorem

**Identifier:** CBF.T51
**Date:** 2026-08-31
**Tier:** exact oriented orthonormal-frame compiler and exact universal
conjugate-paired realification theorem
**Physical status:** the selected q79 Fu-Yau metric, visible-hidden HYM
connection, rank-102 operator, chirality and quantum BV pushforward remain
open.

## 1. The question after T50

CBF.T50 proves an exact statement on the two-dimensional internal profile

```text
R = span{1,nu}.
```

Its normalized Hodge block is

```text
star(1)=nu,
star(nu)=1,
```

and its fiber trace introduces no second density or action primitive. That is
enough for the exact field/antifield profile reduction proved there. It is not
the complete Hodge operator on a six-dimensional compactification and it is
not a real structure on arbitrary bundle-valued fields.

The next question has three parts.

1. Which part of the six-dimensional Hodge operator is universal once an
   oriented orthonormal coframe is supplied?
2. How can a complex bundle-valued field complex be given a canonical real
   carrier without assuming that a chiral bundle is isomorphic to its complex
   conjugate?
3. Does T50's normalized volume determine the remaining Hodge metric?

The answers are respectively: the complete signed exterior table; canonical
conjugate-paired realification; and no.

## 2. Source boundary

The source lock binds the following results.

- H4-T16 supplies the normalized unit/orientation Frobenius block.
- H4-T17 proves that the other 86 bare topology profiles cannot all be removed
  by a degree-one differential on the unchanged topology carrier.
- The q79 degree-two K3 theorem supplies an explicit real double-sextic K3,
  the class `delta=H-L`, and the rank-one Fu-Yau topological skeleton
  `(delta,0)`.
- The q79 K3 real-structure theorem supplies exact complex-conjugation data on
  that K3, but not a Fu-Yau metric.
- The Hodge-action audit already proves that the shared circle alone does not
  select relative Hodge-channel weights. That no-go is inherited here, not
  reproved under a new name.
- The Fourier-Mukai/HYM dependency theorem records that a same-source visible
  line, common visible-hidden HYM endpoint, metric/connection and physical
  `C4` lift remain absent.
- The proto-spinor Hodge table explicitly leaves the oriented full Hodge-star
  wedge-sign table open separately from the metric and HYM coefficients.

This separation is essential. A Hodge sign compiler can be completed without
pretending that its physical metric input has already been selected.

## 3. Complete oriented exterior Hodge table

Let `e1,...,e6` be an oriented orthonormal real coframe and put

```text
nu=e1 wedge e2 wedge e3 wedge e4 wedge e5 wedge e6.
```

For an ordered subset `I` of `{1,...,6}`, let `I^c` be its ordered complement
and let `epsilon(I,I^c)` be the sign of the permutation obtained by listing
`I` followed by `I^c`. Define

```text
star(e_I)=epsilon(I,I^c)e_(I^c).                 (3.1)
```

There are

```text
1+6+15+20+15+6+1=64
```

basis states. Equation (3.1) gives exactly one signed nonzero entry in every
row and every column of the `64 by 64` matrix. The complete table is emitted
in `q79_oriented_hodge_real_carrier.packet.json`; it is not sampled or inferred
from only the unit and orientation entries.

### Theorem 3.1 (full signed-permutation Hodge compiler)

The table (3.1) obeys, for every degree `k`,

```text
star^2=(-1)^(k(6-k)),                             (3.2)
e_I wedge star(e_J)=delta_(I,J) nu                (3.3)
```

whenever `I` and `J` have the same degree. Consequently it is the unique
Hodge operator in the declared oriented orthonormal coframe.

### Proof

Applying (3.1) twice contributes the signs of the two permutations
`(I,I^c)` and `(I^c,I)`. Moving `k` elements past `6-k` elements changes the
sign by `(-1)^(k(6-k))`, proving (3.2).

For equal-cardinality subsets, `e_I wedge e_(J^c)` can be nonzero only if
`I` is contained in `J`; equal cardinality then forces `I=J`. In that case
the wedge permutation sign cancels the sign in (3.1), leaving `nu`. This
proves (3.3). The defining Hodge identity determines the image of every basis
form, proving uniqueness. QED.

The executable certificate checks (3.2) on all 64 basis states and (3.3) on
all 924 equal-degree ordered basis pairs.

## 4. Exact composition with the T50 profile

The degree-zero and degree-six rows of the complete table are

```text
star(1)=nu,
star(nu)=1.                                      (4.1)
```

Thus restriction of the 64-state table to `span{1,nu}` is exactly the T50
Hodge block. With `tau(nu)=1`, the normalized profile metric remains the
identity and the T50 action transport remains

```text
alpha_upper=alpha_lower=f0/hbar.                 (4.2)
```

No volume scalar, trace scalar or second action amplitude is introduced by
extending the sign table from two profiles to all exterior degrees.

This is a composition theorem, not a claim that the 64 exterior-form states
are the same object as the 88 bare topology cohomology profiles or the
rank-102 heterotic deformation carrier. Those three carriers remain typed
separately.

## 5. Equal volume does not select Hodge shape

Fix the standard complex pairs

```text
(e1,e2), (e3,e4), (e5,e6).
```

For `t>0`, define the Hermitian coframe lengths

```text
(t,t,t^(-1),t^(-1),1,1),
```

so that the metric in the fixed coordinate coframe is

```text
g_t=diag(t^2,t^2,t^(-2),t^(-2),1,1).             (5.1)
```

It preserves the fixed complex structure and satisfies

```text
det(g_t)=1,
vol(g_t)=nu.                                      (5.2)
```

For a diagonal metric with coframe lengths `a_i`, the coordinate-basis Hodge
operator is

```text
star_g(e_I)
 = epsilon(I,I^c)
   (product_j a_j)/(product_(i in I) a_i^2)
   e_(I^c).                                       (5.3)
```

At `t=2`, (5.3) gives, among other rows,

```text
star_g(e1)=(1/4)e23456,
star_g(e3)=4e12456,
star_g(1)=nu,
star_g(nu)=1.                                     (5.4)
```

The orientation block and volume are unchanged while the Hodge operator on
intermediate degrees changes.

### Theorem 5.1 (normalized-volume insufficiency)

The normalized T50 density and the shared orientation profile do not select
the full six-dimensional Hodge operator. Even after fixing the complex
structure and volume, the space of positive Hermitian metrics has eight local
real shape directions.

### Proof

Equations (5.2)-(5.4) give an explicit one-parameter counterfamily. More
generally a positive Hermitian `3 by 3` matrix has nine real components, and
unit determinant removes one. Hence the fixed-volume shape space has real
dimension eight. QED.

These eight local metric-shape components are fields or coefficient functions
that a selected Fu-Yau/Strominger solution must compute. They are not eight
new fitted constants and are not added to the parameter ledger.

## 6. Canonical conjugate-paired real carrier

Let `E` be an arbitrary complex vector bundle. A chiral bundle need not admit
an anti-linear involution `E -> E`; requiring one would be an additional and
often false self-conjugacy assumption. Instead define the canonical
realification

```text
R(E)=E direct_sum conjugate(E)                    (6.1)
```

with anti-linear involution

```text
kappa_E(z,w)=(conjugate(w),conjugate(z)).         (6.2)
```

Then

```text
kappa_E^2=1,
Fix(kappa_E)={(z,conjugate(z))}.                  (6.3)
```

If `rank_C(E)=r`, the doubled bundle has complex rank `2r` and its fixed
carrier has real rank `2r`, exactly the real dimension of the original
complex bundle. The conjugate summand is therefore not a second independent
particle family. It is the coordinate-free realification needed to place a
complex field and its conjugate/BV partner in one real carrier.

If `A` is a unitary connection on `E`, equip (6.1) with

```text
nabla_R=nabla_A direct_sum nabla_conjugate(A).    (6.4)
```

Equation (6.2) intertwines the two summands, so

```text
[kappa_E,nabla_R]=0.                              (6.5)
```

The packet contains a rank-three exact Gaussian-rational witness. Its
realified connection is skew-symmetric, commutes with `kappa_E`, and has
fixed and anti-fixed ranks six and six.

This theorem does not identify `E` with `conjugate(E)`, impose a Majorana
condition, select a SpinC lift, or derive chirality. Those require the actual
associated Dirac complex and index data.

## 7. Hodge and Green covariance

Let `Q` be a supplied closed unitary differential on the conjugate-paired
carrier, with a `kappa`-invariant domain and

```text
[kappa,Q]=0.                                      (7.1)
```

Because `kappa` is isometric, (7.1) implies

```text
[kappa,Q*]=0,
[kappa,Delta_Q]=0,
Delta_Q=Q*Q+QQ*.                                  (7.2)
```

Functional calculus then gives

```text
[kappa,P_harmonic]=0.                             (7.3)
```

On the invariant harmonic complement, both `kappa G kappa^(-1)` and `G` are
inverses of `Delta_Q`. Inverse uniqueness gives

```text
[kappa,G]=0.                                      (7.4)
```

Therefore the Hodge homotopy `h=Q*G` also commutes with `kappa` and satisfies

```text
Qh+hQ=1-P_harmonic.                               (7.5)
```

The exact witness checks (7.1)-(7.5), nilpotence, all contraction side
conditions, harmonic rank four and positive rank eight. This is the real
counterpart of the already-proved monodromy inverse-uniqueness result.

Since the exterior Hodge table is real, it acts on the form factor and
commutes with the fiber involution (6.2). Thus a supplied physical HYM
operator can be compiled into a Hodge-real carrier without a further reality
parameter.

## 8. What is q79-specific now

The selected q79 data now supply all of the following at their stated tiers.

```text
explicit real degree-two K3                         exact,
rank-one Fu-Yau topology (delta,0)                  exact topological tier,
K3 complex-conjugation information                  exact,
normalized unit/orientation profile                 exact,
complete six-dimensional exterior Hodge sign table exact compiler,
canonical bundle realification                      exact compiler.
```

They do not yet supply

```text
Fu-Yau conformal factor and Hermitian metric,
selected visible and hidden HYM metrics/connections,
rank-102 Dbar_Q and its closed domains,
physical harmonic projector and reduced Green,
physical C4 HYM lift or direct TT block,
associated first-order chiral operator and index.
```

Accordingly the proto-spinor row

```text
oriented_full_Hodge_star_wedge_sign_table
```

is closed at the universal oriented orthonormal-frame compiler tier. The
separate metric-endomorphism and HYM-connection rows remain open. This is a
strict advance in the dependency graph, not a promotion of the physical
endpoint.

## 9. The 86-mode and chirality boundaries

H4-T17 remains controlling. Its 88-dimensional carrier is bare rational
topology cohomology. The present exterior algebra has 64 pointwise form
states, while the physical heterotic deformation complex has rank 102 before
cohomology and gauge reduction. Equality or substitution among these carriers
is not asserted.

In particular:

- the complete sign table does not make the 86 topology-complement profiles
  massive;
- conjugate-paired realification does not create or remove chiral zero modes;
- a positive Hodge Laplacian does not select a chiral Dirac index;
- the physical spectrum still requires the selected bundle-valued complex.

This preserves both H4-T17's index obstruction and H4-T18's chirality no-go.

## 10. Parameter ledger

```text
shared action primitives before T51: 1,
shared action primitives after T51:  1,
new continuous physical parameters:  0,
new discrete selectors:               0,
observed values used:                 0,
fitted values used:                   0.
```

The eight local metric-shape components in Theorem 5.1 are unresolved source
fields, not accepted free parameters. A physical solution must emit them from
the selected Fu-Yau/HYM equations and certify its domains and errors.

## 11. Frontier delta

CBF.T51 closes two objects that were previously absent:

1. the complete exact 64-state oriented exterior Hodge signed-permutation
   table, including all wedge signs and the T50 orientation restriction;
2. the canonical conjugate-paired real-carrier functor together with exact
   inheritance of a supplied unitary differential, adjoint, Laplacian,
   projector, reduced Green and Hodge homotopy.

It also proves that normalized volume cannot replace the missing metric
source. Therefore the next nonduplicative target is no longer a Hodge sign
table or an abstract reality operation. It is a source-hashed q79 metric and
unitary connection on one selected visible-hidden endpoint, followed by the
rank-102 differential and its symmetry-resolved kernel/Green execution.

The theorem does not select the physical q79 metric, close `B.HS.01`,
`B.GEO.01`, `B.ACTION.01` or `B.QFT.02`, change the H4-T15 global decision, or
move the physical `0/3`, `0/3`, `0/7` counters.

## 12. Reproduction

```powershell
python build_q79_oriented_hodge_real_carrier.py
python verify_q79_oriented_hodge_real_carrier.py
python -m unittest tests.test_q79_oriented_hodge_real_carrier
```

The complete table, exact matrices, source hashes, parameter ledger and claim
boundary are in `q79_oriented_hodge_real_carrier.packet.json`.
