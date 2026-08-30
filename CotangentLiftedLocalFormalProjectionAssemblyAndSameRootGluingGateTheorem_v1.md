# Cotangent-Lifted Local-Formal Projection Assembly and Same-Root Gluing Gate Theorem v1

**Claim:** CBF.T41

**Date:** 2026-08-30

**Status:** exact assembly of the four available local-formal projection
components; exact cotangent-lift and free-shell compatibility theorem; exact
classification and independence of the three missing physical gluing gates;
no selected same-root physical projection, physical tangent metric or
interacting state/BV pushforward is promoted.

## 1. Result

CBF.T40 reduced physical QJ1 and action-jet QJ2 to one source-preserving
pointed quantum projection. Several pieces of such a projection already
exist, but in different typed packages:

```text
T38: radial evaluation and positive state pullback,
T39: anchored action two-jet retraction,
A35: normalized rank-one internal Higgs line,
H4-T15 plus q79 QM: cotangent contraction and free finite-shell BV pushforward.
```

This theorem determines exactly what their conjunction proves.

The four pieces form a consistent **component product**. They do not yet form
a physical projection, because a physical projection is a fiber product over
one source, one physical tangent pairing and one interacting quantum
pushforward. The missing gluing data reduce to three independent gates:

```text
G0  same-root source/action gate,
G1  physical tangent-pairing gate,
G2  selected interacting state/BV gate.                (1.1)
```

The theorem proves that `G0+G1+G2` are necessary and sufficient to promote
the available components to the CBF.T40 `SP0-SP5` object. It also gives exact
countermodels proving that none of the three gates follows from the other
component identities.

This changes the frontier from one undifferentiated request for a projection
map to three typed gluing obligations. It does not change the physical
acceptance counters.

## 2. The four exact components

### 2.1 Radial state component

On a declared q79 local-formal physical algebra `A_phys,H`, T38 defines

```text
A_base=C_0((0,infinity)) tensor A_phys,H,
Pi_H=ev_H tensor id:A_base -> A_phys,H,
Omega_H=omega_H composed with Pi_H.                   (2.1)
```

For every normalized formally positive `omega_H`,

```text
Omega_H(1)=1,
Omega_H(a* a)=omega_H(a(H)* a(H))>=0.                 (2.2)
```

If evaluation commutes with the BRST differential, `Omega_H` is BRST
closed. Its radial marginal is `delta_H`. The q79 state theorem proves that
the allowed local formal state space is nonempty, not that one member is
preferred.

The direction of (2.1) is important. A map of configuration spaces induces
a contravariant map of observable algebras, and states then pull back by
composition. Calling `Pi_H` an algebra projection does not by itself produce
a covariant BV reduction of fields.

### 2.2 Action-jet component

T39 uses

```text
j_H^2 f=(f(H),f'(H),f''(H))                           (2.3)
```

and the finite local counterterm space

```text
C_even=span{1,h^2,h^4}.                              (2.4)
```

For `H>0`, the restriction of (2.3) to (2.4) has determinant `16H^3`.
Therefore it has a unique right inverse `C_H`; the complementary map

```text
R_H=I-C_H                                             (2.5)
```

satisfies

```text
j_H^2 R_H=0,
C_H^2=C_H,
R_H^2=R_H.                                           (2.6)
```

Applied coefficientwise to the local-formal BV scale generator, it preserves
the selected action value, tadpole and Hessian. This is an exact
normalization prescription. It is not yet the result of integrating one
selected upper action.

### 2.3 Rank-one tangent component

A35 supplies the internal line

```text
L_H=span{h0},
<h0,h0>_int=1,                                       (2.7)
```

and the dimensionless insertion

```text
iota_Hnu(h_H)=h_H(I3+X3).                            (2.8)
```

The rank-one projector fixes the dimensionless insertion magnitude. A35
explicitly leaves the physical action weight and dimensionful Dirac readout
open. Thus (2.7) is a coordinate normalization in the selected finite
carrier; it is not yet the wave-function or kinetic metric entering a
four-dimensional repair gradient.

### 2.4 Cotangent and free-shell component

For a normalized contraction

```text
p i=1,
d h+h d=1-i p,
h^2=p h=h i=0,                                      (2.9)
```

H4-T15 proves that

```text
i_hat=i direct-sum p^!,
p_hat=p direct-sum i^!,
h_hat=h direct-sum h^!                               (2.10)
```

is a contraction of the shifted cotangent complexes and preserves the odd
pairing on the retained subspace. A plain projection of a discarded
field-dual pair is not symplectic.

The q79 finite-shell theorem then supplies, after a genuine four-dimensional
BV Hilbert complex and a compatible positive shell have been given,

```text
W_shell=im(Q) direct-sum im(Q^dagger),
L_shell=im(Q^dagger),
h_shell=Q^dagger Delta^-1.                           (2.11)
```

The cycle is Lagrangian, the free quadratic action is nondegenerate and the
finite BV pushforward preserves the free QME up to determinant-line scalar
data. This theorem is exact at free finite-shell tier. It does not construct
the fixed-coupling interacting pushforward or select a state.

## 3. Component product versus physical fiber product

Let

```text
P_sep=P_state x P_jet x P_line x P_BV^free.          (3.1)
```

Equation (3.1) means only that all four certificates are true. Their maps
have compatible formal shapes, but their domains are not identified by a
single source object.

A physical pointed projection must instead contain one upper object

```text
U=(F_up,Q_up,omega_up,S_up,u_*,g_up,r),               (3.2)
```

one lower object

```text
L=(F_H,Q_H,omega_H,Gamma_H,H,g_H),                   (3.3)
```

and one projection/contraction package whose field map, observable pullback,
cotangent lift, action pushforward, state pushforward and tangent derivative
are all induced by the same arrow. The root identifier `r` must pin the
source and every comparison map.

The required diagram is

```text
F_up ----------------p----------------> F_H
 |                                         |
T*[-1]F_up ---------p_hat------------> T*[-1]F_H
 |             BV pushforward              |
S_up, omega_up ----------------------> Gamma_H, omega_H
 |                                         |
T_u*F_up ------------Dp--------------> T_H F_H.       (3.4)
```

The horizontal arrows in (3.4) must commute with the vertical constructions.
Placing unrelated maps next to one another does not make the square commute.

## 4. The three gluing gates

### G0: same-root source/action gate

There must be one root `r`, one upper field/action object and one typed map
whose linear contraction is `(p,i,h)`. Its BV pushforward must emit the lower
effective action. In particular, the T39 retraction must be obtained as the
finite normalization of that pushforward, rather than imposed as an
independent prescription:

```text
Gamma_H=-hbar log integral_LUV exp(-S_up/hbar) rho_up^(1/2),
j_H^2 Gamma_H=j_H^2 S_selected.                      (4.1)
```

All source, action, density, cycle and comparison data must have the same
root hash. This gate includes the field-only action requirement in the
H4-T15 BV compactification contract. A cotangent multiplier action that
vanishes on the zero section cannot replace it.

The same gate must also carry the pointed dynamical square; action
pushforward alone is not presumed to imply it:

```text
p(u_*)=H,
Dp X_up(u_*)=X_Gamma(H),
Dp A_up=A_Gamma Dp on the selected tangent image.     (4.2)
```

### G1: physical tangent-pairing gate

On the selected radial line,

```text
(Dp)^* g_H Dp=g_up,                                  (4.3)
```

and the action Hessians must satisfy

```text
(Dp)^* Hess(Gamma_H)_H Dp=Hess(S_up)_u*.             (4.4)
```

Equation (2.7) supplies a normalized internal coordinate but does not prove
(4.2). A physical kinetic or wave-function pairing is therefore still
needed.

### G2: selected interacting state/BV gate

The same projection must supply a selected interacting QME-preserving BV
pushforward and a selected normalized state satisfying

```text
omega_H=pi_* omega_up,
omega_H(A)=omega_up(pi^* A),                         (4.5)
```

with the declared local-formal or fixed-coupling domain stated explicitly.
The q79 corpus proves nonempty local-formal state spaces and a free
finite-shell pushforward. Neither statement selects the pair in (4.4), and
neither proves the interacting cutoff removal.

## 5. Assembly theorem

### Theorem 5.1: exact promotion criterion

The four components in Section 2 extend to a CBF.T40 source-preserving
pointed quantum projection if and only if `G0`, `G1` and `G2` are supplied
with the typed compatibility equations (4.1)-(4.5).

### Proof

Assume the three gates. `G0` gives one root and the pointed field/action map,
so T40 `SP0` and `SP1` hold. The second and third identities in (4.2) give
`SP2` and `SP3`; they are declared commuting equations, not inferred from an
untyped action integral. Equations (4.3)-(4.4) give `SP4`. The cotangent
lift (2.10), the selected BV pushforward and (4.5) give `SP5`. T40 then
implies physical QJ1 and action-jet QJ2.

Conversely, an `SP0-SP5` object already contains one root, a pointed field
and action projection, tangent isometry, BV/QME pushforward and normalized
state pushforward. Reading these data in the order of (4.1)-(4.5) gives
`G0`, `G1` and `G2`. QED.

The theorem is not an existence proof. It is a necessary-and-sufficient
gluing theorem for the already-available components.

## 6. Independence of the gates

### 6.1 Same-root independence

Take two source labels `r_alpha` and `r_beta` with identical finite matrices,
the same point `H`, the same radial evaluation and isomorphic cotangent
contractions. Every component equation is numerically identical, but no
declared comparison identifies the actions, densities or states across the
two roots. Therefore component equality does not imply `G0`.

This is not metaphysical bookkeeping. A source theorem must distinguish a
derived lower action from an isomorphic action copied in from elsewhere.

### 6.2 Tangent-metric independence

On one real radial line set

```text
Dp=1,
g_up=1,
g_H=lambda^2.                                       (6.1)
```

The state map, action two-jet and cotangent contraction are independent of
`lambda`. The isometry defect is

```text
(Dp)^* g_H Dp-g_up=lambda^2-1.                       (6.2)
```

At the exact witness `lambda=2`, the defect is `3`. Hence `G1` does not
follow from the other components or from the internal unit normalization.

### 6.3 Interacting-state independence

Let the matter algebra be `M_2(C)` and use the two vector states

```text
omega_0(A)=<0|A|0>,
omega_1(A)=<1|A|1>.                                 (6.3)
```

Tensor either state with radial evaluation at `H`. Both extensions are
positive, normalized and have radial marginal `delta_H`. For
`sigma_z=diag(1,-1)`, however,

```text
Omega_0(sigma_z)=1,
Omega_1(sigma_z)=-1.                                (6.4)
```

Thus the exact radial state and all action-jet data do not select a full
matter state. The free-shell BV pushforward also remains true for the common
quadratic complex. This proves that `G2` is independent.

Together, Sections 6.1-6.3 prove that no reordering of the existing component
certificates silently closes the physical projection.

## 7. Exact finite assembly witness

Use the upper primal basis `(r1,r2,u,v)` with

```text
d(u)=v,
p(r1,r2,u,v)=(r1,r2),
i(r1,r2)=(r1,r2,0,0),
h(v)=u.                                              (7.1)
```

The executable verifies all identities in (2.9). On the cotangent lift it
verifies

```text
p_hat i_hat=I4,
d_hat h_hat+h_hat d_hat=I8-i_hat p_hat,
i_hat^T J8 i_hat=J4,
d_hat^T J8+J8 d_hat=0.                              (7.2)
```

The discarded field-dual pair has upper pairing one and projected pairing
zero, so plain deletion fails exactly.

For one contractible shell pair with basis `(e0,e1,f0,f1)`, take

```text
Q e0=e1,
Q f1=-f0.                                           (7.3)
```

Then `Delta=I4`, `h=Q^T`, and `Qh+hQ=I4`. The Hodge cycle
`span{e0,f1}=im(Q^T)` is Lagrangian. The restricted quadratic form has matrix

```text
[[0,-1],[-1,0]]                                     (7.4)
```

and determinant `-1`, proving nondegeneracy.

At `H=3/2`, the action-jet matrix on `(1,h^2,h^4)` has determinant `54`.
The exact polynomial matrices satisfy (2.6). Radial evaluation gives moments
`Omega(h^n)=H^n` and zero variance. Finally, the witnesses (6.2) and (6.4)
execute the independent metric and state defects.

## 8. Clause ledger

The strict physical status is:

| Clause | Available component support | Same-root physical status |
|---|---|---|
| `SP0` | hashes are pinned separately | open: no one root for all maps |
| `SP1` | exact radial evaluation at `H` | open as a physical upper-to-lower map |
| `SP2` | T39 anchored QJ1 scheme | open as a derived action pushforward |
| `SP3` | T39 preserves the action Hessian | open as an operator intertwiner from one source |
| `SP4` | A35 internal unit line | open physical kinetic/wave-function pairing |
| `SP5` | exact cotangent retract, local-formal state existence and free shell pushforward | open selected interacting state/BV pushforward |

Therefore:

```text
component packets assembled:       4/4,
physical gluing gates discharged:  0/3,
physical packets accepted:         0/3,
physical rows accepted:            0/7.              (8.1)
```

The first line is a mathematical assembly result. It must not be substituted
for any of the last three lines.

## 9. Parameter ledger and frontier

This theorem introduces

```text
new continuous physical parameters: 0,
new discrete physical selectors:    0,
new fits:                           0,
new observed inputs:                0.                (9.1)
```

The witness values `H=3/2` and `lambda=2` are exact proof coordinates, not
physical inputs. The finite shell is a proof regulator, not a physical
constant.

Closed here:

- the typed product of all currently available projection components;
- the exact distinction between observable evaluation and BV field
  reduction;
- the cotangent-lift requirement and a nondegenerate free-shell witness;
- a necessary-and-sufficient three-gate promotion theorem; and
- exact independence countermodels for all three gates.

Still open:

- one same-root upper field/action/state object whose pushforward actually
  emits the T39 anchor;
- the physical radial tangent or wave-function metric and its isometry;
- a selected interacting QME-preserving BV pushforward and state;
- the complete q79 BV compactification clauses for charged/chiral fields,
  density, reality, domains and determinant orientation;
- gravitational QJ0, fixed-coupling completion, RG/matching, pole transport
  and held-out observables.

The next constructive target is now precise: build `G0`, because it is the
gate that turns the existing action normalization from an admissible scheme
into a derived same-source result. Its source must simultaneously export the
field-only upper action, BV contraction and radial fixed point. `G1` and `G2`
can then be tested on that actual map rather than on unrelated component
objects.

## 10. Verification

Run:

```powershell
python build_cotangent_lifted_local_formal_projection.py
python verify_cotangent_lifted_local_formal_projection.py
python -m unittest tests.test_cotangent_lifted_local_formal_projection -v
python verify.py
```

The generated packet is
`cotangent_lifted_local_formal_projection.packet.json`.
