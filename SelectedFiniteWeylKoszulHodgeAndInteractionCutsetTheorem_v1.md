# Selected Finite Weyl-Koszul Hodge and Interaction Cutset Theorem v1

**Date:** 2026-08-28  
**Tier:** `SELECTED_EXACT_FINITE + EXACT_INTERACTION_CUTSET`; physical continuum promotion open  
**Parameters fitted:** none  
**Observed physical inputs:** none

## 1. Purpose and source boundary

The q79 total-superconnection program already selects a qutrit Weyl pair
`X,Z`, its conjugation Laplacian

```text
Delta_W=(2-Ad_X-Ad_X*)+(2-Ad_Z-Ad_Z*),
```

the normalized Hilbert-Schmidt pairing, the center projector `P_W`, and the
reduced Green operator `G_W`. What was not yet written down was a differential
whose Hodge Laplacian is exactly this `Delta_W`. Without that differential one
cannot legitimately form `h=d*G`, transfer products, or compare this finite
constraint projector with the completed response operator `D_fin`.

This theorem supplies that missing finite object without changing sources. It
also decides a tempting but false identification: the rank-96 Weyl-center
range is not the rank-96 kernel of `D_fin`. In fact, the two spaces intersect
only at zero.

All consumed artifacts are pinned by repository commit, Git blob and SHA-256
in `q79_weyl_koszul_source_lock.json`. The theorem is finite and exact. It does
not identify this complex with the continuum q79 Dolbeault, HYM or
Hull-Strominger complex.

## 2. The canonical Weyl-Koszul differential

Work over

```text
K=Q(omega),                 omega^2+omega+1=0,
A=M3(K).
```

Let

```text
alpha=Ad_X,                 beta=Ad_Z.
```

Although `ZX=omega XZ`, the two adjoint actions commute because the central
phase cancels:

```text
alpha beta=beta alpha.
```

Introduce two degree-one symbols with relations

```text
theta_x a=alpha(a) theta_x,
theta_z a=beta(a) theta_z,
theta_x^2=theta_z^2=0,
theta_x theta_z=-theta_z theta_x.
```

The resulting 36-dimensional graded algebra is

```text
Omega_W^0=A,
Omega_W^1=A theta_x direct-sum A theta_z,
Omega_W^2=A theta_x theta_z.
```

Define

```text
d(a)=(alpha(a)-a)theta_x+(beta(a)-a)theta_z,
d(theta_x)=d(theta_z)=0,
```

and extend by the graded Leibniz rule. Equivalently,

```text
d0(a)=((alpha-I)a,(beta-I)a),
d1(b,c)=(alpha-I)c-(beta-I)b.
```

Because `alpha` and `beta` commute, `d1 d0=0`; hence `d^2=0`.
The executable proof checks the twisted multiplication on all `36^3=46656`
ordered basis triples, the Leibniz rule on all `36^2=1296` basis pairs and
`d^2=0` on every basis vector. Thus this is an exact DGA, and its graded
commutator is an exact finite DGLA.

The differential is the standard two-generator Koszul differential of the
selected commuting adjoint action. No scalar coefficient or empirical datum
is inserted.

## 3. Hodge theorem

Use the source-selected normalized Hilbert-Schmidt product

```text
<a,b>=Tr(a* b)/3
```

and declare `theta_x,theta_z` orthonormal. On the Weyl mode

```text
W_ab=Z^a X^b
```

The unit orthogonal weights are not an additional fit: they are exactly the
two equal, cross-term-free coefficients already present in the selected
`Delta_W`. A different weighted form metric would define a different
Laplacian and is not used here.

put

```text
p=omega^(-a)-1,             q=omega^b-1.
```

Then the modewise complex is

```text
K --d0--> K^2 --d1--> K,
d0(v)=(pv,qv),              d1(r,s)=ps-qr.
```

Its three Hodge Laplacians are

```text
Delta_0=Delta_W,
Delta_1=diag(Delta_W,Delta_W),
Delta_2=Delta_W.
```

Indeed, on mode `(a,b)` each is scalar multiplication by

```text
s_ab=|p|^2+|q|^2=3[a != 0]+3[b != 0].
```

Therefore the exact spectra are

```text
degree 0: 0^1, 3^4, 6^4,
degree 1: 0^2, 3^8, 6^8,
degree 2: 0^1, 3^4, 6^4.
```

The harmonic projectors, Greens and homotopies are consequently

```text
P0=P_W,                     G0=G_W,
P1=P_W direct-sum P_W,      G1=G_W direct-sum G_W,
P2=P_W,                     G2=G_W,

h1=d0*G1,                   h2=d1*G2.
```

For every nonzero mode,

```text
h1(r,s)=(p* r+q* s)/s_ab,
h2(t)=(-q* t,p* t)/s_ab.
```

Direct exact substitution gives

```text
dh+hd=I-P,                  h^2=0,
Ph=hP=0.
```

Thus

```text
dim H^0=1,                  dim H^1=2,
dim H^2=1.
```

A harmonic basis is `I`, `I theta_x`, `I theta_z`, and
`I theta_x theta_z`. Tensoring with the already-typed
`C3_family tensor H32_SM` spectator gives harmonic ranks

```text
96, 192, 96
```

in degrees zero, one and two. The degree-zero rank 96 is exactly the existing
Weyl-center range. This spectator lift does not turn the complex into the
continuum rank-102 q79 deformation complex.

## 4. Transferred products

The harmonic center is already a sub-DGA:

```text
(I theta_S)(I theta_T)=I(theta_S wedge theta_T).
```

Consequently the transferred binary product is the exterior product. More is
true. Every homological-transfer tree for `m_n`, `n>=3`, contains an internal
edge on which `h` follows a product of harmonic inputs. That product is still
harmonic and `hP=0`. Hence

```text
m2=wedge,                   m_n=0 for every n>=3.
```

This is an exact interaction cutset. The selected finite Weyl constraint
complex supplies `P`, `G` and `h`, but its harmonic center alone does not emit
nonzero higher products. Yukawa, gauge and gravitational interactions must
enter through nonharmonic response lanes, charged coefficient/Hom lanes, the
continuum geometry, or another same-source operation. They cannot be claimed
as hidden higher products of this center complex.

## 5. The two rank-96 spaces are different

The completed finite response uses the source-selected shift polynomial

```text
R_X=(I+X-2X^2)/3,           P_W R_X=(1/3)I.
```

Its excluded component is

```text
Q_W R_X=(X-2X^2)/3 !=0,
```

with exact normalized Hilbert-Schmidt norm squared `5/9`. Since

```text
((L_R_X+R_R_X)/2)(I)=R_X,
```

the nonzero selected shift route sends a center state outside the center.
Therefore `D_fin` does not preserve `Ran(P_phys)`.

There is also a stronger statement. The source theorem gives

```text
T D_fin E=C=(2/3)S_phase+(1/3)S_shift,
S_phase S_shift=S_shift S_phase=0,
S_phase^2+S_shift^2=I32.
```

Hence

```text
C^-1=(3/2)S_phase+3S_shift.
```

If `Ev` belongs to `ker(D_fin)`, then

```text
0=T D_fin E v=Cv,
```

so `v=0`. It follows that

```text
Ran(P_phys) intersect ker(D_fin)={0}.
```

Both spaces have dimension 96, but they are transverse subspaces of the
864-dimensional carrier, not two descriptions of the same finite state space.
The Weyl Hodge projector is the finite constraint-center projector; the
`D_fin` kernel is the zero-mode space of a different completed response
operator. Coupling the two requires the Feshbach/Hodge machinery proved in the
preceding comparison theorem, not a relabeling.

## 6. Cyclic completion and the shared circle

The graded commutator of `Omega_W` is a finite DGLA `L_W`. The source-locked
H4-T14 theorem therefore applies functorially:

```text
L_hat_W=L_W semidirect L_W![-3]
```

has the canonical nondegenerate degree-three evaluation pairing and

```text
S_cot(x,p)=<p,dx+1/2[x,x]>.
```

This adds no free algebraic interaction coefficient. It is a structural
finite cyclic Maurer-Cartan action, not a selected Lorentzian action and not a
compactified Standard Model action.

The shared circle acts centrally on fundamental/projective carriers but
trivially on this adjoint DGLA, exactly as H4-T14 requires. It must not be added
as a third nontrivial Koszul direction merely to retain its phase. A faithful
internal phase requires charged fundamental coefficients or off-diagonal
`Hom(E_i,E_j)` lanes before passing to adjoints.

## 7. What closes and what remains

This theorem closes, at the selected finite tier:

- the differential underlying the existing Weyl Laplacian;
- the complete finite Hodge package `P_W,G_W,h_W` in all degrees;
- the cohomology and all transferred products;
- the exact relationship between the center range and `ker(D_fin)`;
- the canonical structural cyclic cotangent completion.

It does not close:

- the selected continuum q79 Dolbeault/Hull-Strominger differential;
- the physical HYM Hessian, Green kernel or analytic domains;
- a continuum-to-finite cochain and product intertwiner with error bounds;
- charged shared-line matter lanes;
- the Lorentzian action, physical normalization or compactification map;
- blockers `B.GEO.01`, `B.OP.01` or `B.ACTION.01`.

The next mathematically forced target is therefore narrower than before:
construct a selected continuum cochain map whose degree-zero finite shadow is
this Weyl-Koszul contraction and whose response insertion reproduces `D_fin`
through a controlled Feshbach or transferred operator. The finite `P/G/h`
objects no longer need to be guessed.

## 8. Literature boundary

Twisted and skew-derivation calculi are established parts of noncommutative
geometry. Le Stum and Quirós develop differential modules over rings equipped
with families of endomorphisms, while Brzeziński constructs skew-derivation
calculi and Dirac data for generalized Weyl algebras:

- https://arxiv.org/abs/1503.05022
- https://arxiv.org/abs/1602.07456

Accordingly, this theorem does not claim invention of twisted calculus or of
Koszul/Hodge transfer. Its contribution is the source-locked specialization to
the selected finite q79 Weyl pair, the exact identification of the already-used
`Delta_W` as its Hodge Laplacian, the complete transferred-product verdict, and
the transverse rank-96 cutset against `ker(D_fin)`. No external source found in
this comparison supplies those MTT-specific identifications.

## 9. Reproducibility

Run:

```powershell
python build_selected_finite_weyl_koszul_hodge_and_interaction_cutset.py
python verify_selected_finite_weyl_koszul_hodge_and_interaction_cutset.py
```

The builder uses exact rational arithmetic in `Q(omega)`. The verifier has an
independent implementation and does not import the builder.
