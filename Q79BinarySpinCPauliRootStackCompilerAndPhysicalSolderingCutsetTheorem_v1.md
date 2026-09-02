# Q79 Binary-SpinC Pauli Root-Stack Compiler and Physical-Soldering Cutset Theorem v1

**Claim:** `CBF.T62`
**Date:** 2026-09-02
**Status:** `CLOSED EXACT FLAT ROOT-STACK 1+3 COMPILER; QUTRIT SOURCE IDENTIFICATION AND PHYSICAL HYM SOLDERING OPEN`

## 1. Result

`CBF.T61` found the correct local algebra behind the proposed complex nesting:
a determinant-twisted copy of `End(C^2)` decomposes as one scalar direction
plus three traceless Pauli directions. It left open whether this local `1+3`
object is globally the q79 shared line plus the rank-three sheet carrier.

This theorem closes that question on the selected flat root-stack carrier.
Let `S` be the complex rank-two spinor carrier of the already selected binary
sheet lift and let

```text
D=det(S).
```

Then the determinant-twisted Pauli object has an exact `S3`-equivariant
decomposition

```text
D tensor End(S)
  = D tensor C I2  direct-sum  D tensor sl(S)
  = L_shared       direct-sum  E_D^C.                 (1.1)
```

Here `L_shared` is the selected flat shared/SpinC determinant line and `E_D`
is the q79 rank-three sheet-permutation local system. The proof is not a
dimension match: the two determinant-twisted adjoint matrices are literally
the two standard permutation matrices generating `S3`.

The two conjugate shared roots `+i` and `-i` induce the same compiler. Their
scalar phases cancel on `End(S)`, and both have determinant character `sign`.
No root selector and no parameter is added.

The theorem also sharpens the remaining boundary. Equation (1.1) is a global
flat-root-stack symbol theorem, not the physical q79 HYM endpoint. To compose
it with the `CBF.T61` double-qutrit source and the `CBF.T58` augmented symbol,
one still needs:

```text
b_v:U_v -> S,                 b_i:U_i -> S,            (1.2)
tau:D tensor End(S) -> augmented degree one,           (1.3)
sigma_D:E_D^C -> T^(0,1)*X.                            (1.4)
```

The maps in (1.2) must come from the same selected Fourier-Mukai/internal
qutrit source. The degree map (1.3) must be an actual suspension or
totalization of the mixed degree-two summand. The soldering (1.4) must be
unitary and parallel for the selected visible-hidden HYM connection, extend
through ramification and preserve the physical symbol, domains and residual.

## 2. Exact binary carrier

Use the quaternion basis `1,i,j,k` and put `r=sqrt(2)/2`. The selected binary
sheet generators are

```text
q1=r(i-j),                    q2=r(j-k).                (2.1)
```

Direct quaternion multiplication gives

```text
q1^2=q2^2=-1,
q1 q2 q1=q2 q1 q2,
(q1 q2)^3=-1.                                         (2.2)
```

Thus they generate the nonsplit binary extension `Dic3` of `S3`. Combining
either generator with either common phase root gives

```text
u_a^+=+i q_a,                  u_a^-=-i q_a,
(u_a^+)^2=(u_a^-)^2=1.                                 (2.3)
```

The central signs cancel in the SpinC quotient. Both branches obey the
ordinary `S3` involution and braid relations. Complex conjugation exchanges
the two branches; it does not change any endomorphism or determinant-twisted
adjoint row below.

## 3. Pauli adjoint

Represent a quaternion `a+bi+cj+dk` on `S=C^2` by

```text
rho(a+bi+cj+dk)
 = [[a+ib, c+id],[-c+id,a-ib]].                        (3.1)
```

On the ordered Pauli basis `(sigma_x,sigma_y,sigma_z)`, conjugation by
`rho(q1)` and `rho(q2)` is

```text
A1=[[-1, 0, 0],               A2=[[ 0,-1, 0],
    [ 0, 0,-1],                   [-1, 0, 0],
    [ 0,-1, 0]],                  [ 0, 0,-1]].          (3.2)
```

Each transposition has determinant `-1` on `S`, so `D` contributes one more
minus sign. Therefore

```text
B1=-A1=[[1,0,0],              B2=-A2=[[0,1,0],
        [0,0,1],                      [1,0,0],
        [0,1,0]],                     [0,0,1]].         (3.3)
```

But `B1=P_(23)` and `B2=P_(12)` exactly. Hence

```text
D tensor sl(S) = E_D^C                                  (3.4)
```

as a flat associated bundle with its full `S3` holonomy, not merely as an
abstract rank-three vector bundle. The character checks are

```text
chi_sl(S)          = (3,-1,0) = chi_(sign tensor E_D),
chi_(D tensor sl)  = (3, 1,0) = chi_E_D,               (3.5)
```

on identity, transposition and three-cycle classes.

## 4. Scalar line and complete 1+3 action

The scalar matrix is fixed by conjugation. Tensoring it by `D` gives the sign
line:

```text
D tensor C I2 = D = L_shared.                           (4.1)
```

For the two generating transpositions, the complete compiler action on the
ordered basis `(I2,sigma_x,sigma_y,sigma_z)` is

```text
R1=diag(-1,P_(23)),             R2=diag(-1,P_(12)).     (4.2)
```

These matrices generate six and only six elements. Their character is

```text
chi_(D direct-sum E_D)=(4,0,1).                         (4.3)
```

The scalar line in (4.1) is the same root-independent order-two restriction
of the universal flat `Z64` line already identified with the q79 SpinC
determinant. This closes the `d_alpha`-type comparison only for the flat
root-stack augmented line. It does not identify that line with the physical
cotangent-symbol line of `CBF.T58`.

## 5. Relation to the q79 strain carrier

`CBF.T42` proves that the determinant-twisted harmonic plane, after tensoring
by `E_D`, is the two-copy q79 `D/E` strain local system

```text
E_D direct-sum E_S
```

with parallel complex structure

```text
J_DE=[[0,-I3],[I3,0]].                                  (5.1)
```

Equation (3.4) identifies the Pauli three-lane with the same `E_D` source.
Realifying its complex coefficients supplies the two real copies on which
`J_DE` acts. Thus the binary-Pauli compiler and the earlier root-plane strain
functor meet on one exact flat associated local system.

This is the correct place to use the shared circle. It supplies the
determinant/SpinC sign and its quarter-root presentation; it is not a geometric
rotation exchanging the marked Fu-Yau circle directions. The marked vertical
`C4` no-go remains untouched.

## 6. Hidden HYM compatibility

The locked hidden-side HYM theorem proves

```text
W_sh=L_shared tensor W9,
nabla_sh=nabla_L tensor I9 + I tensor nabla_W,           (6.1)
End(W_sh)=End(W9).                                      (6.2)
```

Because the shared-line connection is scalar and flat, it cancels from the
adjoint commutator. Curvature, the projective HYM constant, the hidden adjoint
connection and the hidden deformation/Hessian block are unchanged. Therefore
the scalar line of (1.1) is compatible with the already closed existential
hidden projective HYM object.

This is not a common visible-hidden endpoint. The visible `V3`, common chamber,
pointwise Bianchi identity, differential Green-Schwarz data and numerical HYM
connection remain open under `B.HS.01`.

## 7. Why T24 does not yet supply the degree shift

`CBF.T24` proves a unique Koszul totalization of an external degree-one
closure differential with the root-neutral order-zero finite Yukawa incidence.
Its selected operator has the form

```text
q_tot=q_Y tensor I + Gamma_Y tensor q_F.                (7.1)
```

The T61 Pauli source instead lies in the mixed bidegree `(1,1)` summand

```text
U_v tensor U_i subset Lambda^2(U_v direct-sum U_i).     (7.2)
```

Equation (7.1) neither suspends (7.2) nor identifies it with the augmented
degree-one carrier. Reusing T24 as that map would change the grading and the
factor types without a universal property. Consequently T24 closes the
shared-line parallelism pattern but not the T61 degree shift. The required
`tau` in (1.3) remains a genuine source object.

## 8. Exact source cutset

The global problem is now factored into three independent layers.

### 8.1 Closed flat compiler

```text
selected binary SpinC carrier S
  -> D=det(S)=L_shared
  -> D tensor End(S)
  -> L_shared direct-sum E_D^C.                         (8.1)
```

Every arrow in (8.1) is exact, root independent, parameter free and parallel
for the selected flat root-stack connection.

### 8.2 Open same-source qutrit binding

T60 selects two qutrit factors with different geometric jobs. One is the
relative theta/Fourier-Mukai factor; the other is the internal projective
qutrit over the identity. Their marked local `X/Z` planes have the same local
matrix form, but the existing packets do not supply global parallel maps
`b_v,b_i` in (1.2) to the binary sheet spinor carrier. Setting them equal by
notation would be the same unsupported globalization that T61 forbids.

Once both maps are emitted, the T61 matching becomes

```text
s=b_v^(-1) b_i                                           (8.2)
```

and is selected rather than chosen from `U(2) x U(2)`.

### 8.3 Open physical soldering

The final physical map is reduced to

```text
L_shared direct-sum E_D^C
   --(line comparison direct-sum sigma_D)-->
L_alpha direct-sum T^(0,1)*X.                           (8.3)
```

It must intertwine the selected continuum connection and complete holonomy,
not just `S3` and the flat root-stack connection. It must also preserve the
metric, orientation, principal symbol, domains, projector, reduced Green
operator and certified continuum-to-finite residual.

## 9. Frontier and parameter ledger

Closed here:

- the exact binary quaternion and SpinC return relations;
- the determinant character of the binary spinor carrier;
- the literal Pauli-adjoint matrices and their determinant twist;
- the global flat-root-stack identity
  `D tensor End(S)=L_shared direct-sum E_D^C`;
- root independence of the complete `1+3` compiler;
- compatibility of its scalar line with hidden shared-line HYM tensoring;
- the proof that T24 is not the missing T61 suspension.

Still open:

- the two same-source qutrit-to-binary maps `b_v,b_i`;
- a selected suspension/totalization `tau` for the mixed degree-two source;
- the physical line comparison and HYM soldering `sigma_D`;
- the selected visible/common Hull-Strominger endpoint;
- the physical Hessian, projector, Green operator, residual and interval
  certificate.

Accordingly `B.HS.01`, `B.GEO.01` and `B.OP.01` remain open, and physical
acceptance remains `0/3` packets and `0/7` rows.

```text
new observed inputs:                 0
new fitted values:                   0
new continuous physical parameters: 0
new discrete physical selectors:    0
unselected conjugate root branches: 2 equivalent presentations
```

The frontier change is real but bounded: the abstract determinant-twisted
Pauli possibility in T61 is now a constructed global flat q79 `1+3` compiler.
The remaining unknown is no longer its representation or shared-line
monodromy; it is the same-source qutrit binding, degree shift and physical HYM
soldering.

## 10. Reproduction

```powershell
python build_q79_binary_spinc_pauli_rootstack_compiler.py
python verify_q79_binary_spinc_pauli_rootstack_compiler.py
python -m unittest tests.test_q79_binary_spinc_pauli_rootstack_compiler -v
```

The generated packet is
`q79_binary_spinc_pauli_rootstack_compiler.packet.json`.
