# q79 Double-Qutrit Polarization, Mixed-Bidegree Endomorphism and SpinC Soldering Criterion Theorem v1

**Claim:** `CBF.T61`

**Date:** 2026-09-01

**Status:** exact selected chartwise polarization of the T60 degree-one
carrier, exact mixed-bidegree endomorphism and Pauli decomposition, and exact
global connection/soldering criterion. The selected physical q79 HYM
intertwiner, endpoint Hessian and Green operator remain open.

## 1. Result and boundary

CBF.T60 proves that the two selected qutrit factors supply four finite Koszul
directions and that their exterior dimensions equal the five correction ranks
of the complete augmented heterotic symbol in CBF.T58:

```text
1, 4, 6, 4, 1.
```

It correctly refuses to promote this rank identity through an arbitrary
`U(4)` map. This theorem resolves the local algebraic part and separates two
different constructions that had been in danger of being conflated.

1. The original degree-one carrier has an exact holomorphic polarization.
   The vertical-theta `+i` line is one-dimensional and its orthogonal
   complement has dimension three. The marked vertical/internal labels and
   the locked eta9 `X/Z` orientation fix this transform chartwise. Thus the
   local generic `U(4)` search is unnecessary.
2. The mixed bidegree `(1,1)` inside finite degree two is also rank four. Its
   two quarter-turn signs cancel, and it is canonically an endomorphism
   carrier. It has the exact trace/traceless decomposition

   ```text
   M2(C)=C I2 direct-sum sl2(C),
   4=1+3.
   ```

   The normalized Pauli transform is explicit and unitary.
3. These are not the same bridge. The first preserves T60's exterior degree.
   The second is the natural SpinC-adjoint candidate but lies in finite degree
   two. Using it as T58's degree-one generator requires a selected
   suspension or totalization map; a dimension match cannot supply that
   shift.
4. Global physical promotion is now an exact bundle problem. The same-degree
   route requires a parallel line map `s_alpha` and a parallel rank-three map
   `kappa_3`. The mixed route requires a parallel identification of the two
   qutrit planes, an adjoint/SpinC soldering and the degree shift. Holonomy,
   curvature and characteristic-class identities below decide these claims.

No physical row is accepted here. `B.HS.01`, `B.GEO.01` and `B.OP.01` remain
open. The advance is that their former local `U(4)` ambiguity has been
replaced by explicit maps and falsifiable global equations.

## 2. Locked finite planes

Let

```text
U_v=span_C(theta_vX,theta_vZ),
U_i=span_C(theta_iX,theta_iZ).                       (2.1)
```

The subscripts distinguish the vertical Fourier-Mukai theta action from the
internal qutrit action over the identity. CBF.T60 proves that these actions
have different geometric jobs; this theorem never identifies them as the
same translation.

The selected Fourier cohomology action in the ordered `X/Z` basis is

```text
    [ 0 -1 ]
J = [      ],              J^2=-I2.                  (2.2)
    [ 1  0 ]
```

Thus the four-dimensional degree-one carrier is

```text
F1=U_v direct-sum U_i,
J1=J direct-sum J,
J1^2=-I4.                                             (2.3)
```

The `+i` and `-i` eigendirections are

```text
theta_a^+=(theta_aX-i theta_aZ)/sqrt(2),
theta_a^-=(theta_aX+i theta_aZ)/sqrt(2),
a=v,i.                                                (2.4)
```

They are orthonormal for the T60 exterior metric.

## 3. Same-degree polarized bridge

Order the polarized basis as

```text
(theta_v^+, theta_i^+, theta_v^-, theta_i^-).         (3.1)
```

For coefficient columns in the original ordered basis, the coefficient
transform is `H_pol=N_pol/sqrt(2)`, where

```text
        [ 1   i   0   0 ]
        [ 0   0   1   i ]
N_pol = [ 1  -i   0   0 ].                            (3.2)
        [ 0   0   1  -i ]
```

Exact multiplication gives

```text
N_pol N_pol^*=2I4,
det(N_pol)=4,                                         (3.3)
```

and

```text
H_pol J1 H_pol^-1=diag(i,i,-i,-i).                   (3.4)
```

The selected chartwise `1+3` split is therefore

```text
L_fin   =span(theta_v^+),
R3_fin  =span(theta_i^+,theta_v^-,theta_i^-),
F1=L_fin direct-sum R3_fin.                           (3.5)
```

This uses the fact that T60 already distinguishes the vertical theta factor
from the internal factor. It also uses the eta9 complex orientation to name
the holomorphic sign. Reversing that orientation gives the conjugate `-i`
line. That is the existing conjugate shared-line pair, not a fitted physical
number.

Equation (3.5) closes the local linear-map selection problem while preserving
the original finite exterior degree. It does not yet produce a global q79
bundle map. The finite Fourier `C4` is a global harmonic/root-stack symmetry
at its proved tier but not a selected autonomous symmetry of the physical
marked Fu-Yau HYM complex.

## 4. Why the direct carrier is not the adjoint carrier

There is a second possible meaning of `1+3`: a scalar plus the adjoint of a
rank-two spinor bundle. Under a spinorial quarter-turn, the central square
`-I2` acts trivially on endomorphisms. The corresponding tensorial action
therefore squares to `+I4`.

No invertible map can intertwine (2.3) with that action, because similarity
preserves squares:

```text
J1^2=-I4,                 J_tensor^2=+I4.             (4.1)
```

This is an exact no-go only for treating direct degree one as the doubled
SpinC-adjoint carrier. It is not a no-go for the polarized bridge in Section
3, whose target action has eigenvalues `+i,+i,-i,-i`. It also does not infer
an unproved physical `C4` action on T58.

## 5. Mixed bidegree and double return

The degree-two cohomology decomposes canonically as

```text
Lambda^2(U_v direct-sum U_i)
 =Lambda^2 U_v
  direct-sum (U_v tensor U_i)
  direct-sum Lambda^2 U_i,                            (5.1)
```

with ranks

```text
1+4+1=6.                                              (5.2)
```

On the mixed summand, the diagonal return is `J tensor J`, so

```text
(J tensor J)^2=(-I) tensor (-I)=+I.                  (5.3)
```

This is the precise finite form of a double traversal: each qutrit plane is
spinorial under the quarter-turn, while their mixed tensor is tensorial. It
has eigenvalue multiplicities

```text
(+1)^2, (-1)^2.                                       (5.4)
```

Let

```text
          [ 0  1 ]
epsilon = [       ].                                  (5.5)
          [-1  0 ]
```

Then `J^T epsilon J=epsilon`. In marked bases define

```text
Phi(u tensor v)=u v^T epsilon.                        (5.6)
```

This is a signed permutation of the four orthonormal matrix units, hence a
unitary map to `M2(C)`. Symplectic covariance gives

```text
Phi(Ju tensor Jv)=J Phi(u tensor v) J^-1.             (5.7)
```

The two central signs have disappeared by tensoring rather than by being
discarded.

## 6. Exact trace and Pauli transform

Use the orthonormal Hermitian basis

```text
tau_0=I2/sqrt(2),
tau_1=sigma_1/sqrt(2),
tau_2=sigma_2/sqrt(2),
tau_3=sigma_3/sqrt(2).                                (6.1)
```

In the mixed basis

```text
(vX tensor iX, vX tensor iZ,
 vZ tensor iX, vZ tensor iZ),                         (6.2)
```

the coefficient transform is `H=N/sqrt(2)` with

```text
    [ 0  -1   1   0 ]
    [ 1   0   0  -1 ]
N = [ i   0   0   i ].                                (6.3)
    [ 0  -1  -1   0 ]
```

Exact calculation gives

```text
N N^*=2I4,             det(N)=4i.                    (6.4)
```

The rows are

```text
scalar:   (-vX_iZ+vZ_iX)/sqrt(2),
sigma_1:  ( vX_iX-vZ_iZ)/sqrt(2),
sigma_2:  i(vX_iX+vZ_iZ)/sqrt(2),
sigma_3:  (-vX_iZ-vZ_iX)/sqrt(2).                    (6.5)
```

Under the doubled return,

```text
H(J tensor J)H^-1=diag(1,-1,1,-1).                   (6.6)
```

Thus the trace line is fixed, one traceless Pauli direction is fixed, and two
are odd. The alternative conjugate sign for `sigma_2` is the already-present
`+i/-i` shared-line pair; it does not add a numerical knob.

## 7. Globalization of the mixed carrier

The formula (5.6) is global only after its bundle typing is respected. Let
`U_v` and `U_i` now denote Hermitian rank-two bundles with their selected
connections, and write `D_i=det(U_i)`. The raw mixed bundle is

```text
M=U_v tensor U_i.                                     (7.1)
```

For every rank-two bundle there is a canonical variance-changing identity

```text
U_i = U_i^* tensor D_i,                               (7.2)
```

given by `v -> (w -> v wedge w)`. Consequently the globally correct form of
the local matrix carrier is

```text
M=Hom(U_i,U_v) tensor D_i.                            (7.3)
```

The local epsilon in (5.5) is a local frame of `D_i^*`; it must not be used
as an undeclared global determinant trivialization. This determinant twist is
the exact place where the shared circle can enter the mixed construction.

A trace splitting in (7.3) additionally requires a unitary
determinant-compatible isomorphism

```text
s:U_i -> U_v.                                         (7.4)
```

It is connection-compatible precisely when

```text
nabla_v s-s nabla_i=0.                                (7.5)
```

Equivalently, for every loop `gamma`,

```text
Hol_v(gamma)s=s Hol_i(gamma),                         (7.6)
```

and necessarily

```text
F_v s=s F_i.                                          (7.7)
```

When (7.4)-(7.5) hold,

```text
M=D_i tensor C s
  direct-sum D_i tensor Hom_0^s(U_i,U_v),             (7.8)
Hom_0^s={A:tr(s^-1 A)=0}.                             (7.9)
```

The scalar lane is therefore `D_i`, not a globally constant copy of `C`. A
physical mixed bridge needs a parallel shared-line map

```text
d_alpha:D_i -> L_alpha.                              (7.10)
```

The locked sources give a marked `X/Z` matching chartwise. They do not prove
(7.3): the first qutrit comes from relative theta translation, whereas the
second is an internal projective action over the identity. The source packets
explicitly do not identify those extensions or emit their connection
matrices.

The finite `C4` test alone cannot select `s`. The complex intertwiner space
between the two multiplicity-`2+2` representations has dimension eight, and
the unitary family is `U(2) x U(2)`. Fixing the scalar line still leaves
`U(1) x U(2)`. The connection and full source holonomy, not `C4` by itself,
must remove this freedom. This is the correct use of the holonomy criterion:
curvature generates restricted holonomy, so a parallel bridge must
intertwine the full transported curvature algebra.

## 8. SpinC/adjoint soldering criterion

After (7.4), the traceless mixed bundle is
`D_i tensor End_0(U_v)`. To identify it with the three-dimensional form lane
in T58 requires

```text
kappa:D_i tensor End_0(U_v) -> T^(0,1)*X.            (8.1)
```

The physical claim needs (8.1) to be complex linear, metric and orientation
preserving, parallel, and equivariant under the selected monodromy or the
direct TT action. Its connection and curvature equations are

```text
nabla_T kappa(delta tensor B)
 =kappa(nabla_D delta tensor B
        +delta tensor [nabla_v,B]),                   (8.2)

F_T kappa(delta tensor B)
 =kappa(F_D delta tensor B
        +delta tensor [F_v,B]).                       (8.3)
```

For a rank-two bundle `W` with formal Chern roots `x_1,x_2`, `End_0(W)` has
roots

```text
0, x_1-x_2, x_2-x_1.
```

Let `l=c1(D_i)`. Tensoring the three adjoint roots by `D_i` gives roots

```text
l, l+x_1-x_2, l+x_2-x_1.
```

Consequently a necessary topological test for (8.1) is

```text
c1(T^(0,1)*X)=3l,
c2(T^(0,1)*X)=3l^2+4c2(W)-c1(W)^2,
c3(T^(0,1)*X)=l^3+l(4c2(W)-c1(W)^2).                 (8.4)
```

These conditions are necessary, not sufficient. A bundle can pass them and
still fail the connection-holonomy test. Conversely, equality of dimensions
does not imply any line of (8.4). If `D_i` is parallel-trivial, `l=0` and
(8.4) reduces to the untwisted formulas
`c1=0`, `c2=4c2(W)-c1(W)^2`, `c3=0`; that special case must be proved rather
than assumed.

This is exactly the missing proto-spinor language in complex rank three: one
rank-two bundle must simultaneously carry the shared determinant line and
have its traceless endomorphisms soldered to the selected three-dimensional
geometric carrier. The theorem supplies the criterion, not the selected q79
solution.

## 9. The two physical bridge formulas

### 9.1 Same-degree route

Let `L_alpha` be the normalized T58 symbol line spanned by
`alpha_hat=alpha/|alpha|`. The direct route requires parallel unitary maps

```text
s_alpha:L_fin -> L_alpha,
kappa_3:R3_fin -> T^(0,1)*X.                         (9.1)
```

Then

```text
I_pol=s_alpha direct-sum kappa_3                    (9.2)
```

is a unitary `1+3` map. Its exterior powers, followed by T60's exact map
`J_n`, intertwine all five abstract correction carriers while retaining the
original degree.

### 9.2 Mixed SpinC route

If (7.4), (7.10) and (8.1) are supplied, write locally

```text
A=delta tensor B,
b_0=tr(B)/2,
B_0=B-b_0 I2.                                        (9.3)
```

The normalized local isometry is

```text
I_mix(delta tensor B)
 =tr(B)/sqrt(2) d_alpha(delta)
  direct-sum kappa(delta tensor B_0).                 (9.4)
```

It sends `delta tensor s/sqrt(2)` to `d_alpha(delta)`. But its source is the
mixed `(1,1)` summand of finite degree two. Equation (9.4) becomes a T58
generator map only after a source-selected suspension or totalization
identifies that summand with the augmented degree-one carrier. This theorem
does not insert that shift by hand.

For either route, a smooth bounded unitary bundle map transports the standard
Sobolev spaces on compact `X`. Equality of the actual operator domains and
lower-order blocks requires the selected endpoint. The remaining operator
defect is the concrete expression

```text
R_I=H_aug I-I H_fin.                                  (9.5)
```

It cannot be evaluated before the q79 HYM Hessian coefficients and
connections are emitted.

## 10. Frontier change

Closed exactly:

- the same-degree chartwise holomorphic `1+3` polarization of T60's four
  finite one-forms;
- the no-go for interpreting direct degree one as the doubled-return
  SpinC-adjoint carrier;
- the rank-four mixed-bidegree replacement and central-sign cancellation;
- its unitary endomorphism, trace/traceless and Pauli maps;
- the determinant-line twist required to globalize that local matrix map;
- the exact holonomy, curvature and Chern tests for global promotion;
- the two correctly typed physical bridge formulas and their degree
  distinction.

Still open:

- a parallel global `s_alpha` and `kappa_3` for the same-degree route;
- or a parallel qutrit matching `s`, determinant/shared-line map `d_alpha`,
  determinant-twisted SpinC soldering `kappa` and selected totalization shift
  for the mixed route;
- the common visible/hidden Hull-Strominger endpoint and explicit
  connections;
- the physical Hessian, harmonic projector, reduced Green, domain and error
  certificate.

Therefore the generic local `U(4)` search is retired, but no physical gate or
row moves. The next computation is no longer another basis search. It is the
holonomy/curvature comparison for the two maps in (9.1); in parallel, (8.4)
is the first inexpensive global cutset for the mixed SpinC route.

## 11. Parameters and reproduction

```text
new continuous physical parameters: 0
new discrete physical selectors:    0
observed values used:                0
fitted values used:                  0
```

Run:

```powershell
python build_q79_double_qutrit_mixed_bidegree_spinc_soldering.py
python verify_q79_double_qutrit_mixed_bidegree_spinc_soldering.py
python -m unittest tests.test_q79_double_qutrit_mixed_bidegree_spinc_soldering -v
```

The connection criterion is consistent with the Ambrose-Singer holonomy
theorem:

- W. Ambrose and I. M. Singer, *A theorem on holonomy*, Transactions of the
  American Mathematical Society 75 (1953), 428-443,
  https://doi.org/10.1090/S0002-9947-1953-0063739-1.

The executable packet is
`q79_double_qutrit_mixed_bidegree_spinc_soldering.packet.json`.
